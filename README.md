# 16×16 Sudoku base dataset Release

在 GitHub Actions → **Import 16x16 Sudoku Base Dataset** → **Run workflow** 執行。

Workflow 只稀疏下載上游 `base/16x16`（10,000 題），讀取 `.sdk.txt` 和 `.sdk.json` 的 `solution_grid`，檢查所有答案符合 16×16 Sudoku 規則、提示與答案一致、上游標記 minimal、無完全重複題目，然後發布 Release。

## Release

- `base16.bin`：12-byte header + 10,000 × 160-byte records = **1,600,012 bytes**。
- `manifest.json`：上游 commit、檔案大小、SHA-256。
- `UPSTREAM_LICENSE.txt`：原資料集 MIT 授權。

## base16.bin v1

Header: bytes 0..3 `S16B`；bytes 4..5 little-endian uint16 version=1；bytes 6..7 uint16 record_size=160；bytes 8..11 uint32 count=10000。

每筆 160 bytes：前 128 bytes 為完整解答，每格 4 bits（高 nibble 先），值 0..15 對應數字 1..16；後 32 bytes 是 256 個提示格 bitmask（每 byte MSB 先），1 代表顯示該格答案，0 代表空格。第 i 筆 record offset = 12 + i*160，i 從 0 開始。

Android 使用者端可以隨機從 0 bit 中選擇若干格改為 1，新增的提示值直接來自完整答案，因此保留唯一解。這不保證難度標籤準確。

## SHA-256 更新

App 取得固定 tag 的 manifest 或 GitHub API 最新 Release manifest，與本機 `base16.bin` SHA-256 比較；不同才下載，下載到暫存檔並再次驗證 hash，成功後原子替換。若要避免遭竄改，manifest 本身也需可信來源／簽章。

## 唯一解保證範圍

上游 README 宣稱 base/16x16 每題有唯一解且為 minimal。本工具驗證盤面規則、提示與解答相符及上游 minimal metadata，但**不重新執行獨立唯一解求解器**；若需要完全獨立驗證，可另加 solver 驗證步驟。
