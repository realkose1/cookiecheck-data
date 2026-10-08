/* 쿠키이써 — 현재 상영작.
   자동 생성 파일입니다. 직접 고치지 말고 `python3 tools/fetch_movies.py` 를 실행하세요.
   작품 정보: TMDB /movie/now_playing?region=KR (조회일 2026-10-08)
   관객수: KOBIS 일별 박스오피스 (기준일 20261007)
   쿠키 정보: aftercredits.com + 나무위키 + 자동 조사 + TMDB 키워드 + data.overrides.json */

const DATA_UPDATED = '2026-10-08';
const BOXOFFICE_DATE = "20261007";

const MOVIES = [
  {
    "id": "the-odyssey",
    "tmdbId": 1368337,
    "title": "오디세이",
    "meta": "모험 · 액션 · 판타지",
    "meta2": "173분",
    "posterPath": "/8ze9OcVuFiy94s6FFPvsn4oC2e1.jpg",
    "releaseDate": "2026-08-05",
    "audience": 12068518,
    "boRank": 4,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/07/odyssey-the-2026/"
  },
  {
    "id": "tmdb-1418428",
    "tmdbId": 1418428,
    "title": "암살자(들)",
    "meta": "드라마 · 범죄 · 스릴러",
    "meta2": "131분",
    "posterPath": "/c55ijsOdntj6P25vDwHLdgsBpmV.jpg",
    "releaseDate": "2026-09-23",
    "audience": 2520869,
    "boRank": 1,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "desc": "메인 크레딧이 모두 올라간 뒤 쿠키 영상 1개가 나온다. 주연 배우와 제작진 이름이 전부 지나간 시점에서 실제 뉴스 생방송 영상이 등장하며, 영화가 다룬 1974년 8월 15일 저격 사건의 실제 뉴스 화면으로 보인다.",
        "len": "",
        "pos": "크레딧 종료 후"
      }
    ],
    "tip": "",
    "source": "wikitree.co.kr · gukjenews.com (자동 조사)",
    "sourceUrl": "https://www.wikitree.co.kr/articles/1161295"
  },
  {
    "id": "tmdb-1394740",
    "tmdbId": 1394740,
    "title": "타짜: 벨제붑의 노래",
    "meta": "범죄 · 드라마",
    "meta2": "130분",
    "posterPath": "/ueigb5zra1tj6FTK9yhh2P33P9B.jpg",
    "releaseDate": "2026-09-23",
    "audience": 1520782,
    "boRank": 3,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "gukjenews.com (자동 조사)",
    "sourceUrl": "https://www.gukjenews.com/news/articleView.html?idxno=3705531"
  },
  {
    "id": "obsession",
    "tmdbId": 1339713,
    "title": "옵세션",
    "meta": "공포 · 스릴러",
    "meta2": "109분",
    "posterPath": "/df4rpubfWy0g7HCzBNtPLLKnoMH.jpg",
    "releaseDate": "2026-09-02",
    "audience": 934139,
    "boRank": 10,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/05/obsession-2025/"
  },
  {
    "id": "tmdb-607833",
    "tmdbId": 607833,
    "title": "인턴",
    "meta": "드라마 · 코미디",
    "meta2": "133분",
    "posterPath": "/nPu9o9yHwN8Gu2Yc1av6KKMbXZf.jpg",
    "releaseDate": "2026-09-16",
    "audience": 853944,
    "boRank": 7,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 종료 후",
        "len": "",
        "desc": "엔딩 크레딧이 모두 올라간 뒤 쿠키 영상이 한 편 이어집니다. 장면 내용은 공개되지 않았습니다."
      }
    ],
    "tip": "",
    "source": "언론 보도 (금강일보·이투데이·국제뉴스)",
    "sourceUrl": "https://www.ggilbo.com/news/articleView.html?idxno=1181861"
  },
  {
    "id": "tmdb-1586876",
    "tmdbId": 1586876,
    "title": "극장판 치이카와: 인어 섬의 비밀",
    "meta": "애니메이션 · 가족 · 모험",
    "meta2": "99분",
    "posterPath": "/5TMyytCI5Pfc9c1eNsljiCdiB05.jpg",
    "releaseDate": "2026-09-30",
    "audience": 818352,
    "boRank": 2,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "위치 미확인",
        "len": "",
        "desc": "엔딩 후 쿠키 영상이 있으며 그게 진짜 결말이므로 스태프롤이 끝나기 전에 영화관을 나가지 않는 것이 좋다."
      }
    ],
    "tip": "",
    "source": "나무위키",
    "sourceUrl": "https://namu.wiki/w/%EA%B7%B9%EC%9E%A5%ED%8C%90%20%EC%B9%98%EC%9D%B4%EC%B9%B4%EC%99%80%3A%20%EC%9D%B8%EC%96%B4%20%EC%84%AC%EC%9D%98%20%EB%B9%84%EB%B0%80"
  },
  {
    "id": "tmdb-961214",
    "tmdbId": 961214,
    "title": "부활남: 더 레드",
    "meta": "액션 · 판타지",
    "meta2": "102분",
    "posterPath": "/nLsyRK3SmtdIftozpCd8sGQMRGD.jpg",
    "releaseDate": "2026-09-30",
    "audience": 243832,
    "boRank": 6,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "gukjenews.com (자동 조사)",
    "sourceUrl": "https://www.gukjenews.com/news/articleView.html?idxno=3710851"
  },
  {
    "id": "digger",
    "tmdbId": 1248832,
    "title": "디거",
    "meta": "코미디 · 드라마",
    "meta2": "129분",
    "posterPath": "/jV5Mfasg8dP3XK5nuXLetBN3APx.jpg",
    "releaseDate": "2026-10-03",
    "audience": 49719,
    "boRank": 8,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "엔딩 크레딧 전반부는 극장 밖 장면 위로 흘러가며, 홍수로 인한 잔해와 거대한 방조제로 가득 찬 디스토피아적인 도시의 모습을 보여줍니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/10/digger-2026/"
  },
  {
    "id": "tmdb-1587473",
    "tmdbId": 1587473,
    "title": "입에 대한 앙케트",
    "meta": "공포",
    "meta2": "89분",
    "posterPath": "/ioogrqn2xtQjZBuHpNXPb8qtaQG.jpg",
    "releaseDate": "2026-10-07",
    "audience": 8416,
    "boRank": 5,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "tmdb-1280738",
    "tmdbId": 1280738,
    "title": "퓨리어스",
    "meta": "액션 · 범죄 · 스릴러",
    "meta2": "114분",
    "posterPath": "/x959xPUa6DebrSj2xNtF0NYSiCm.jpg",
    "releaseDate": "2026-10-07",
    "audience": 3941,
    "boRank": 9,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/06/furious-the-2025/"
  },
  {
    "id": "tmdb-1591675",
    "tmdbId": 1591675,
    "title": "룩백",
    "meta": "드라마",
    "meta2": "101분",
    "posterPath": "/mAfcD0lspaNlZDRrzT0fdWS5C01.jpg",
    "releaseDate": "2026-10-08",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "ghost-in-the-cell",
    "tmdbId": 1393326,
    "title": "고스트 인 더 셀",
    "meta": "공포 · 코미디 · 스릴러",
    "meta2": "106분",
    "posterPath": "/coyrg56aluVoOUS69ciZgnn5FIy.jpg",
    "releaseDate": "2026-10-07",
    "audience": null,
    "boRank": null,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "크레딧 중간에 장면이 있습니다."
      },
      {
        "pos": "크레딧 종료 후",
        "len": "",
        "desc": "크레딧이 끝난 뒤 장면이 있습니다."
      }
    ],
    "tip": "",
    "source": "TMDB 키워드",
    "sourceUrl": "https://www.themoviedb.org/movie/1393326"
  },
  {
    "id": "la-valle-dei-sorrisi",
    "tmdbId": 1092936,
    "title": "홀리보이",
    "meta": "스릴러 · 드라마 · 판타지",
    "meta2": "123분",
    "posterPath": "/vxkPiWdut20cHrFW57nduhhMR2V.jpg",
    "releaseDate": "2026-10-07",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "above-below",
    "tmdbId": 1514682,
    "title": "카르텔 오션",
    "meta": "스릴러 · 범죄",
    "meta2": "96분",
    "posterPath": "/zxTQqW2BYaBjLIvdfkXNnVfpfB3.jpg",
    "releaseDate": "2026-09-30",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "tmdb-1305781",
    "tmdbId": 1305781,
    "title": "표인: 풍기대막",
    "meta": "액션 · 모험",
    "meta2": "127분",
    "posterPath": "/yVEwJ0Badf4KYhhXNRNa8MIkgKP.jpg",
    "releaseDate": "2026-09-30",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "linkin-park-unshatter",
    "tmdbId": 1388805,
    "title": "언섀터",
    "meta": "음악 · 다큐멘터리",
    "meta2": "108분",
    "posterPath": "/l4YDO15cNt7wnWs9wX1vSzmW9bn.jpg",
    "releaseDate": "2026-09-30",
    "audience": null,
    "boRank": null,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 종료 후",
        "len": "",
        "desc": "크레딧이 끝난 뒤 장면이 있습니다."
      }
    ],
    "tip": "",
    "source": "TMDB 키워드",
    "sourceUrl": "https://www.themoviedb.org/movie/1388805"
  },
  {
    "id": "stitch-head",
    "tmdbId": 1214130,
    "title": "스티치 헤드: 비밀의 성 꼬마괴물",
    "meta": "애니메이션 · 모험 · 가족",
    "meta2": "92분",
    "posterPath": "/dTcAE69YKmEatDPCl1BmOpFHbUb.jpg",
    "releaseDate": "2026-09-30",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "alpha",
    "tmdbId": 1284460,
    "title": "알파",
    "meta": "공포 · 드라마 · SF",
    "meta2": "128분",
    "posterPath": "/tUZaajRDFjitxzCQK87vlRDedox.jpg",
    "releaseDate": "2026-09-30",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/03/alpha-2025/"
  },
  {
    "id": "l-tranger",
    "tmdbId": 1429348,
    "title": "이방인",
    "meta": "드라마 · 범죄",
    "meta2": "123분",
    "posterPath": "/2NoWaSTgKF7FcJ0Lr5NrvDDINOv.jpg",
    "releaseDate": "2026-09-30",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "forgotten-island",
    "tmdbId": 1465063,
    "title": "포가튼 아일랜드",
    "meta": "애니메이션 · 모험 · 판타지",
    "meta2": "109분",
    "posterPath": "/bIQY9RLkqUhdwOBExK4k3ggxddF.jpg",
    "releaseDate": "2026-09-23",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/09/forgotten-island-2026/"
  },
  {
    "id": "tmdb-1483525",
    "tmdbId": 1483525,
    "title": "가능한 사랑",
    "meta": "드라마",
    "meta2": "165분",
    "posterPath": "/7UAzxqezg5yvZyK3k62wOAzg0Zs.jpg",
    "releaseDate": "2026-09-23",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "gukjenews.com · wikitree.co.kr (자동 조사)",
    "sourceUrl": "https://www.gukjenews.com/news/articleView.html?idxno=3705818"
  },
  {
    "id": "late-fame",
    "tmdbId": 1285895,
    "title": "나의 사적인 예술가",
    "meta": "드라마",
    "meta2": "96분",
    "posterPath": "/hv7zKr3cCdOFhNVcqWYj74Ij6KX.jpg",
    "releaseDate": "2026-09-23",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/08/late-fame-2025/"
  }
];

const INITIAL_VOTES = {
  "the-odyssey": {
    "up": 0,
    "down": 0
  },
  "tmdb-1418428": {
    "up": 0,
    "down": 0
  },
  "tmdb-1394740": {
    "up": 0,
    "down": 0
  },
  "obsession": {
    "up": 0,
    "down": 0
  },
  "tmdb-607833": {
    "up": 0,
    "down": 0
  },
  "tmdb-1586876": {
    "up": 0,
    "down": 0
  },
  "tmdb-961214": {
    "up": 0,
    "down": 0
  },
  "digger": {
    "up": 0,
    "down": 0
  },
  "tmdb-1587473": {
    "up": 0,
    "down": 0
  },
  "tmdb-1280738": {
    "up": 0,
    "down": 0
  },
  "tmdb-1591675": {
    "up": 0,
    "down": 0
  },
  "ghost-in-the-cell": {
    "up": 0,
    "down": 0
  },
  "la-valle-dei-sorrisi": {
    "up": 0,
    "down": 0
  },
  "above-below": {
    "up": 0,
    "down": 0
  },
  "tmdb-1305781": {
    "up": 0,
    "down": 0
  },
  "linkin-park-unshatter": {
    "up": 0,
    "down": 0
  },
  "stitch-head": {
    "up": 0,
    "down": 0
  },
  "alpha": {
    "up": 0,
    "down": 0
  },
  "l-tranger": {
    "up": 0,
    "down": 0
  },
  "forgotten-island": {
    "up": 0,
    "down": 0
  },
  "tmdb-1483525": {
    "up": 0,
    "down": 0
  },
  "late-fame": {
    "up": 0,
    "down": 0
  }
};
