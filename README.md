# cookiecheck-data

[쿠키이써] 앱의 데이터 피드. 매일 자정(KST) GitHub Actions 가
`tools/fetch_movies.py` 를 돌려 `cookies.json` 을 갱신한다 — 앱은 실행할 때마다
`https://raw.githubusercontent.com/realkose1/cookiecheck-data/main/cookies.json` 을 읽는다.

- 작품 정보: TMDB `/movie/now_playing?region=KR` · 관객수: KOBIS 일별 박스오피스
- 쿠키 정보: aftercredits.com(`data/ac-index.json` 색인) + 나무위키 + `data.overrides.json`(수동 확정)
- 갱신 로직·소스별 판정 규칙은 본 저장소 `tools/` 와 앱 저장소 README 참고

수동 실행: Actions 탭 → refresh → Run workflow.
