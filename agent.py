name: Gunluk Borsa Ozeti

on:
  schedule:
    - cron: "0 5 * * 1-5"   # 05:00 UTC = 08:00 Türkiye, hafta içi
  workflow_dispatch:         # elle çalıştırma düğmesi

permissions:
  contents: read
  issues: write

jobs:
  ozet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Ozeti uret
        run: python3 agent.py
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

      - name: Kayit ac (mail olarak gelir)
        run: |
          gh issue create \
            --title "Borsa Özeti $(date +'%d.%m.%Y')" \
            --body-file ozet.md \
            --assignee "${{ github.repository_owner }}"
        env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
