#include <stdio.h>
#include <string.h>

#define MAXN 52

typedef struct {
    int up, down, left, right;
} Dir;

typedef struct {
    int row, col, deg;
    Dir dir;
} Connector;

int n, m;
int grid[MAXN][MAXN];
Connector connectors[MAXN * MAXN];
int conn_count = 0;
int used[MAXN][MAXN][4]; // 0:up, 1:down, 2:left, 3:right

// Directions: up, down, left, right
const int dr[4] = {-1, 1, 0, 0};
const int dc[4] = {0, 0, -1, 1};

int in_grid(int r, int c) {
    return r >= 1 && r <= n && c >= 1 && c <= m;
}

// Try to connect all connectors recursively
int dfs(int idx) {
    if (idx == conn_count) {
        // Check if all connectors have correct degree
        for (int i = 0; i < conn_count; ++i) {
            int cnt = connectors[i].dir.up + connectors[i].dir.down +
                      connectors[i].dir.left + connectors[i].dir.right;
            if (cnt != connectors[i].deg) return 0;
        }
        return 1;
    }

    int r = connectors[idx].row;
    int c = connectors[idx].col;
    int deg = connectors[idx].deg;

    // Try all possible combinations of directions
    // There are at most 4 directions, so 2^4 = 16 combinations
    for (int mask = 0; mask < 16; ++mask) {
        int up = (mask >> 3) & 1;
        int down = (mask >> 2) & 1;
        int left = (mask >> 1) & 1;
        int right = (mask >> 0) & 1;
        if (up + down + left + right != deg) continue;

        // Check if the directions are valid (no double use)
        int valid = 1;
        int nr, nc;
        // up
        if (up) {
            nr = r + dr[0];
            nc = c + dc[0];
            if (!in_grid(nr, nc) || !grid[nr][nc]) { valid = 0; break; }
            if (used[r][c][0] || used[nr][nc][1]) { valid = 0; break; }
        }
        // down
        if (down) {
            nr = r + dr[1];
            nc = c + dc[1];
            if (!in_grid(nr, nc) || !grid[nr][nc]) { valid = 0; break; }
            if (used[r][c][1] || used[nr][nc][0]) { valid = 0; break; }
        }
        // left
        if (left) {
            nr = r + dr[2];
            nc = c + dc[2];
            if (!in_grid(nr, nc) || !grid[nr][nc]) { valid = 0; break; }
            if (used[r][c][2] || used[nr][nc][3]) { valid = 0; break; }
        }
        // right
        if (right) {
            nr = r + dr[3];
            nc = c + dc[3];
            if (!in_grid(nr, nc) || !grid[nr][nc]) { valid = 0; break; }
            if (used[r][c][3] || used[nr][nc][2]) { valid = 0; break; }
        }
        if (!valid) continue;

        // Mark
        if (up) { used[r][c][0] = 1; used[r+dr[0]][c+dc[0]][1] = 1; }
        if (down) { used[r][c][1] = 1; used[r+dr[1]][c+dc[1]][0] = 1; }
        if (left) { used[r][c][2] = 1; used[r+dr[2]][c+dc[2]][3] = 1; }
        if (right) { used[r][c][3] = 1; used[r+dr[3]][c+dc[3]][2] = 1; }
        connectors[idx].dir.up = up;
        connectors[idx].dir.down = down;
        connectors[idx].dir.left = left;
        connectors[idx].dir.right = right;

        if (dfs(idx + 1)) return 1;

        // Unmark
        if (up) { used[r][c][0] = 0; used[r+dr[0]][c+dc[0]][1] = 0; }
        if (down) { used[r][c][1] = 0; used[r+dr[1]][c+dc[1]][0] = 0; }
        if (left) { used[r][c][2] = 0; used[r+dr[2]][c+dc[2]][3] = 0; }
        if (right) { used[r][c][3] = 0; used[r+dr[3]][c+dc[3]][2] = 0; }
    }
    return 0;
}

int main() {
    // Read input
    if (scanf("%d %d", &n, &m) != 2) return 1;
    memset(grid, 0, sizeof(grid));
    memset(used, 0, sizeof(used));
    conn_count = 0;

    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= m; ++j) {
            int v;
            if (scanf("%d", &v) != 1) return 1;
            grid[i][j] = v;
            if (v > 0) {
                connectors[conn_count].row = i;
                connectors[conn_count].col = j;
                connectors[conn_count].deg = v;
                connectors[conn_count].dir.up = 0;
                connectors[conn_count].dir.down = 0;
                connectors[conn_count].dir.left = 0;
                connectors[conn_count].dir.right = 0;
                conn_count++;
            }
        }
    }

    if (!dfs(0)) {
        printf("No Solution\n");
        return 0;
    }

    // Output in row-major order, left to right
    for (int i = 0; i < conn_count; ++i) {
        printf("%d %d %d %d %d %d\n",
            connectors[i].row, connectors[i].col,
            connectors[i].dir.up, connectors[i].dir.down,
            connectors[i].dir.left, connectors[i].dir.right
        );
    }
    return 0;
}
