/* 쿠키이써 — 현재 상영작.
   자동 생성 파일입니다. 직접 고치지 말고 `python3 tools/fetch_movies.py` 를 실행하세요.
   작품 정보: TMDB /movie/now_playing?region=KR (조회일 2026-10-06)
   관객수: KOBIS 일별 박스오피스 (기준일 20261005)
   쿠키 정보: aftercredits.com + 나무위키 + 자동 조사 + TMDB 키워드 + data.overrides.json */

const DATA_UPDATED = '2026-10-06';
const BOXOFFICE_DATE = "20261005";

const MOVIES = [
  {
    "id": "the-odyssey",
    "tmdbId": 1368337,
    "title": "오디세이",
    "meta": "모험 · 액션 · 판타지",
    "meta2": "173분",
    "posterPath": "/8ze9OcVuFiy94s6FFPvsn4oC2e1.jpg",
    "releaseDate": "2026-08-05",
    "audience": 12045159,
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
    "audience": 2412815,
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
    "audience": 1462358,
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
    "audience": 926973,
    "boRank": 7,
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
    "audience": 844383,
    "boRank": 8,
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
    "audience": 736036,
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
    "audience": 225892,
    "boRank": 5,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "avengers-endgame",
    "tmdbId": 299534,
    "title": "어벤져스: 엔드게임",
    "meta": "모험 · SF · 액션",
    "meta2": "181분",
    "posterPath": "/z7ilT5rNN9kDo8JZmgyhM6ej2xv.jpg",
    "releaseDate": "2019-04-24",
    "audience": 157616,
    "boRank": 9,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "2026년 9월 25일 재재개봉: 원작 영화에서처럼, 스티브 로저스와 페기 카터가 집에서 춤을 추는 장면이 나옵니다. 하지만 두 사람이 입을 맞추려는 순간, 문을 두드리는 소리가 들립니다. 스티브가 옆방 문가에 숨은 채, 페기가 문을 엽니다. 로키가 들어와 두 사람 모두를 도와줄 수 있다고 말합니다.\n브루스 배너는 콘크리트로 된 방에서 영상 기록을 남기고 있습니다. 그는 지난 2년 동안 군사 시설 지하 2마일 아래에 있었기 때문에 자신은 나갈 수 없고 아무도 들어올 수 없다고 설명합니다. 그가 실험 중인 새로운 감마 치료법에 대해 설명하던 중, 커다란 소음과 전자 간섭이 녹화를 방해하기 시작합니다. 화면이 끊기지만, 닥터 둠이 그를 데리러 왔다고 말하는 목소리가 들립니다.\nIMAX 인피니티 비전 상영관에서만: 마지막 장면은 시간변동관리국(TVA)에서 펼쳐집니다. 모비우스가 통제 센터로 들어가 우주들이 서로 붕괴하고 있다는 보고를 접합니다. 장면이 끝날 무렵, 3000개의 우주가 붕괴했다는 보고가 들어옵니다. 다중우주가 제거되고 있는 것으로 보입니다."
      },
      {
        "pos": "크레딧 종료 후",
        "len": "",
        "desc": "금속끼리 부딪히는 소리가 들립니다.\n개봉 2주 후, 영화 '스파이더맨: 파 프롬 홈'의 예고편이 상영됩니다.\n\n\n2019년 6월 28일 재개봉:\n\n스탠 리를 추모하는 영상이 나오는데, 그의 카메오 출연에 대해 이야기하는 인터뷰가 포함되어 있습니다. \"Stan We Love You 3000\"이라는 문구로 마무리됩니다.\n공동 감독 앤소니 루소가 삭제된 장면을 소개합니다: \"끝까지 자리를 지켜주셔서 감사합니다... 아시다시피 이 영화에는 정말 많은 것을 담았습니다. 많은 캐릭터, 많은 액션, 많은 감정, 그리고 제 생각엔 많은 즐거움까지도요. 하지만 믿기 힘들겠지만 편집 과정에서 잘라내야 했던 장면들이 있습니다. 그렇습니다, 영화는 훨씬 더 길어질 수도 있었죠.\"\n미완성 '삭제된 장면'에서는 헐크가 위성 접시로 불타는 건물에서 사람들을 구하고, 현장의 응급 지원 요원에게 전화를 건네받아 \"스티브가 누구야?\"라고 묻습니다. 경찰관 역할은 '다이 하드'의 레지널드 벨존슨이 카메오로 출연합니다.\n화면에 \"그리고 한 가지 더…\"라는 메시지가 나타납니다.\n차가 멕시코 익스텐코 사막으로 들어갑니다. 마리아 힐과 닉 퓨리가 '얼굴 달린 사이클론'이 일으킨 사건을 조사하며 미스테리오를 소개하고 \"이 일에는 절대 끼어들지 않는 게 좋을 거야\"라고 말합니다.\n마지막으로 화면에 \"마블 스튜디오 전 직원을 대신하여 / 감사합니다\"라는 메시지가 나타납니다.\n\n2026년 9월 25일 재재개봉:\n금속끼리 부딪히는 소리 이후, 닥터 둠의 마스크가 보이고 이어서 닥터 둠 본인이 등장합니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2019/04/avengers-endgame-2019/"
  },
  {
    "id": "digger",
    "tmdbId": 1248832,
    "title": "디거",
    "meta": "코미디 · 드라마",
    "meta2": "129분",
    "posterPath": "/jV5Mfasg8dP3XK5nuXLetBN3APx.jpg",
    "releaseDate": "2026-10-03",
    "audience": 40399,
    "boRank": 6,
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
    "id": "tmdb-1765609",
    "tmdbId": 1765609,
    "title": "극장판 래브라도: 망고축제를 지켜라",
    "meta": "애니메이션 · 가족",
    "meta2": "64분",
    "posterPath": "/44c7U4ipQfJZ8pWmb9cJKy99jAL.jpg",
    "releaseDate": "2026-10-03",
    "audience": 21086,
    "boRank": 10,
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
  },
  {
    "id": "familiar-touch",
    "tmdbId": 1265717,
    "title": "친숙한 손길",
    "meta": "드라마",
    "meta2": "92분",
    "posterPath": "/4tWJdFTBEg0hXHw41ZFCjj3Cvpo.jpg",
    "releaseDate": "2026-09-23",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "dead-shot",
    "tmdbId": 507250,
    "title": "데드 샷",
    "meta": "액션 · 스릴러",
    "meta2": "92분",
    "posterPath": "/4K98Uxar2JwQarF7uijSUcHKyhW.jpg",
    "releaseDate": "2026-09-22",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "resident-evil",
    "tmdbId": 1423191,
    "title": "레지던트 이블: 0번째 밤",
    "meta": "공포 · SF · 모험",
    "meta2": "94분",
    "posterPath": "/fQX4fRsagskLvCXnvPfdvh62QTG.jpg",
    "releaseDate": "2026-09-17",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "SlashFilm",
    "sourceUrl": "https://www.slashfilm.com/2260289/resident-evil-2026-movie-post-credits-scene-guide/"
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
  "avengers-endgame": {
    "up": 0,
    "down": 0
  },
  "digger": {
    "up": 0,
    "down": 0
  },
  "tmdb-1765609": {
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
  },
  "familiar-touch": {
    "up": 0,
    "down": 0
  },
  "dead-shot": {
    "up": 0,
    "down": 0
  },
  "resident-evil": {
    "up": 0,
    "down": 0
  }
};
