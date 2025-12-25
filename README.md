# Tarot Ledger

간단한 커맨드라인 타로 장부 도구입니다. JSON 파일에 리딩 기록을 저장하며, 질문, 카드, 스프레드, 노트를 함께 관리할 수 있습니다.

## 주요 기능
- `add`: 새 리딩 추가 (날짜, 질문, 뽑은 카드, 스프레드, 노트)
- `list`: 날짜 범위로 리딩 목록 조회
- `summary`: 전체 리딩 수와 가장 자주 나온 카드 Top 3 표시

## 사용 방법
Python 3만 있으면 별도 의존성 없이 실행할 수 있습니다.

```bash
python tarot_ledger.py add --question "오늘의 조언은?" --cards "The Fool, The Sun, Nine of Cups" \\
  --spread "3장" --notes "긍정적인 에너지" --date 2024-05-10

python tarot_ledger.py list --from 2024-01-01 --to 2024-12-31

python tarot_ledger.py summary
```

기본 저장 파일은 같은 디렉터리의 `ledger.json`입니다. 다른 위치를 사용하려면 `--file` 옵션으로 경로를 지정하세요.
