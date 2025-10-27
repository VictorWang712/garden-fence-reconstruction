#include <stdio.h>
#include <string.h>

#define MAXN 52

typedef struct {
    int row, col, deg; // Store row, column, and degree for each connector 
    int dir[4]; // Directions: 0:up, 1:down, 2:left, 3:right; 1 means selected 
} Connector;

int n, m; // Grid dimensions 
int grid[MAXN][MAXN]; // 0: empty, >0: connector 
Connector connectors[MAXN * MAXN]; // Array of connectors 
int conn_count = 0; // Number of connectors 

const int dr[4] = {-1, 1, 0, 0}; // Row deltas for directions 
const int dc[4] = {0, 0, -1, 1}; // Column deltas for directions 

int next_conn[MAXN * MAXN][4]; // Next connector in each direction for each connector 

int fence[MAXN][MAXN]; // 0: none, 1: vertical, 2: horizontal 

int used[MAXN * MAXN][4]; // Whether a direction has been paired for each connector 

int conn_idx[MAXN][MAXN]; // Map from grid position to connector index 

int in_grid(int r, int c) { // Check if (r, c) is inside the grid 
    return r >= 0 && r < n && c >= 0 && c < m; // Return 1 if inside, 0 otherwise 
}

void precompute_next() { // Precompute the next connector in each direction 
    memset(next_conn, -1, sizeof(next_conn)); // Initialize all to -1 (no connector) 
    for (int i = 0; i < conn_count; ++i) { // For each connector 
        int r = connectors[i].row; // Get row of connector 
        int c = connectors[i].col; // Get column of connector 
        for (int d = 0; d < 4; ++d) { // For each direction 
            int nr = r + dr[d], nc = c + dc[d]; // Move to next cell in direction 
            while (in_grid(nr, nc)) { // While inside grid 
                if (grid[nr][nc] > 0) { // If there is a connector 
                    next_conn[i][d] = conn_idx[nr][nc]; // Store its index 
                    break; // Stop searching in this direction 
                }
                nr += dr[d]; // Move further in the same direction 
                nc += dc[d]; // Move further in the same direction 
            }
        }
    }
}

int can_place_fence(int r, int c, int d) { // Check if a fence can be placed at (r, c) in direction d 
    if (fence[r][c] == 0) return 1; // If no fence, can place 
    if ((d == 0 || d == 1) && fence[r][c] == 1) return 1; // Vertical allowed 
    if ((d == 2 || d == 3) && fence[r][c] == 2) return 1; // Horizontal allowed 
    return 0; // Otherwise, cannot place 
}

void mark_fence(int r0, int c0, int r1, int c1, int d, int val) { // Mark or unmark a fence path 
    int r = r0 + dr[d], c = c0 + dc[d]; // Start at next cell in direction 
    while (r != r1 || c != c1) { // Until reaching the target 
        if (grid[r][c] == 0) { // Only mark if not a connector 
            fence[r][c] = val; // Set the fence value 
        }
        r += dr[d]; // Move in direction 
        c += dc[d]; // Move in direction 
    }
}

int count_dir(int idx) { // Count how many directions are used for a connector 
    int cnt = 0; // Initialize counter 
    for (int d = 0; d < 4; ++d) cnt += connectors[idx].dir[d]; // Add up used directions 
    return cnt; // Return the count 
}

int dfs(int idx) { // Depth-first search for solution 
    if (idx == conn_count) { // If all connectors processed 
        for (int i = 0; i < conn_count; ++i) { // For each connector 
            int cnt = 0; // Count used directions 
            for (int d = 0; d < 4; ++d) cnt += connectors[i].dir[d]; // Sum up 
            if (cnt != connectors[i].deg) return 0; // Degree not matched 
        }
        return 1; // All degrees matched 
    }
    if (count_dir(idx) == connectors[idx].deg) { // If current connector is full 
        return dfs(idx + 1); // Move to next connector 
    }
    for (int d = 0; d < 4; ++d) { // For each direction 
        if (connectors[idx].dir[d]) continue; // Skip if already used 
        int j = next_conn[idx][d]; // Get next connector in this direction 
        if (j == -1) continue; // No connector found 
        int od = d ^ 1; // Opposite direction 
        if (used[idx][d] || used[j][od]) continue; // Skip if already paired 
        if (count_dir(j) == connectors[j].deg) continue; // Skip if other is full 
        int r0 = connectors[idx].row, c0 = connectors[idx].col; // Start position 
        int r1 = connectors[j].row, c1 = connectors[j].col; // End position 
        int r = r0 + dr[d], c = c0 + dc[d]; // Move to next cell 
        int valid = 1; // Assume path is valid 
        while (r != r1 || c != c1) { // Check path 
            if (grid[r][c] > 0) { valid = 0; break; } // Blocked by connector 
            if (!can_place_fence(r, c, d)) { valid = 0; break; } // Fence conflict 
            r += dr[d]; // Move in direction 
            c += dc[d]; // Move in direction 
        }
        if (!valid) continue; // Skip if path invalid 
        connectors[idx].dir[d] = 1; // Mark direction used 
        connectors[j].dir[od] = 1; // Mark opposite direction used 
        used[idx][d] = 1; // Mark as used 
        used[j][od] = 1; // Mark as used 
        int val = (d < 2) ? 1 : 2; // 1 for vertical, 2 for horizontal 
        mark_fence(r0, c0, r1, c1, d, val); // Mark the fence 
        if (dfs(idx)) return 1; // Continue filling current connector 
        connectors[idx].dir[d] = 0; // Undo direction 
        connectors[j].dir[od] = 0; // Undo opposite direction 
        used[idx][d] = 0; // Undo used 
        used[j][od] = 0; // Undo used 
        mark_fence(r0, c0, r1, c1, d, 0); // Remove the fence 
    }
    if (count_dir(idx) == connectors[idx].deg) { // If filled after trying 
        if (dfs(idx + 1)) return 1; // Try next connector 
    }
    return 0; // No solution found here 
}

int main() {
    if (scanf("%d %d", &n, &m) != 2) return 1; // Read grid size 
    memset(grid, 0, sizeof(grid)); // Initialize grid 
    memset(conn_idx, -1, sizeof(conn_idx)); // Initialize connector index map 
    conn_count = 0; // Reset connector count 
    for (int i = 0; i < n; ++i) { // For each row 
        for (int j = 0; j < m; ++j) { // For each column 
            int v; // Value for cell 
            if (scanf("%d", &v) != 1) return 1; // Read cell value 
            grid[i][j] = v; // Store in grid 
            if (v > 0) { // If it's a connector 
                connectors[conn_count].row = i; // Store row 
                connectors[conn_count].col = j; // Store column 
                connectors[conn_count].deg = v; // Store degree 
                for (int d = 0; d < 4; ++d) connectors[conn_count].dir[d] = 0; // Initialize directions 
                conn_idx[i][j] = conn_count; // Map position to index 
                conn_count++; // Increment connector count 
            }
        }
    }
    memset(fence, 0, sizeof(fence)); // Initialize fence array 
    memset(used, 0, sizeof(used)); // Initialize used array 
    precompute_next(); // Precompute next connectors 
    if (!dfs(0)) { // Start DFS from first connector 
        printf("No Solution\n"); // Print if no solution 
        return 0; // Exit 
    }
    for (int i = 0; i < conn_count; ++i) { // For each connector 
        printf("%d %d %d %d %d %d\n",
            connectors[i].row + 1, connectors[i].col + 1, // Output row and column (1-based) 
            connectors[i].dir[0], connectors[i].dir[1], // Output up and down 
            connectors[i].dir[2], connectors[i].dir[3] // Output left and right 
        );
    }
    return 0;
}
