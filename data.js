/* 쿠키이써 — 현재 상영작.
   자동 생성 파일입니다. 직접 고치지 말고 `python3 tools/fetch_movies.py` 를 실행하세요.
   작품 정보: TMDB /movie/now_playing?region=KR (조회일 2026-08-31)
   관객수: KOBIS 일별 박스오피스 (기준일 20260830)
   쿠키 정보: aftercredits.com + 나무위키 + TMDB 키워드 + data.overrides.json */

const DATA_UPDATED = '2026-08-31';
const BOXOFFICE_DATE = "20260830";

const MOVIES = [
  {
    "id": "the-odyssey",
    "tmdbId": 1368337,
    "title": "오디세이",
    "meta": "모험 · 액션 · 판타지",
    "meta2": "173분",
    "posterPath": "/8ze9OcVuFiy94s6FFPvsn4oC2e1.jpg",
    "releaseDate": "2026-08-05",
    "audience": 8864932,
    "boRank": 1,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/07/odyssey-the-2026/"
  },
  {
    "id": "spider-man-brand-new-day",
    "tmdbId": 969681,
    "title": "스파이더맨: 브랜드 뉴 데이",
    "meta": "SF · 액션 · 모험",
    "meta2": "145분",
    "posterPath": "/8mLepBa5l591xFidRpn65xV7hb4.jpg",
    "releaseDate": "2026-07-29",
    "audience": 8548398,
    "boRank": 2,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "뉴욕에서 일상을 보내는 사람들의 배경 이미지들이 나옵니다."
      },
      {
        "pos": "크레딧 종료 후",
        "len": "",
        "desc": "스파이디 트래커가 새로운 '알 수 없는 위치'에서 스파이더맨을 '발견'합니다. 트래커 화면이 뉴욕에서 대륙, 지구 전체로 줌아웃되다가 달을 살짝 지나 우주까지 나아가는데, 이때 '스파이더맨: 뉴 유니버스'의 글리치 연출과 같은 효과로 화면이 지지직거립니다. 그리고 새로운 스파이더맨의 위치가 우주임을 표시합니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/07/spider-man-brand-new-day-2026/"
  },
  {
    "id": "tmdb-1436168",
    "tmdbId": 1436168,
    "title": "사랑의 하츄핑: 고래보석의 전설",
    "meta": "애니메이션 · 가족 · 모험",
    "meta2": "105분",
    "posterPath": "/tmV1b9s0zKtUx06pkYaRtBAz065.jpg",
    "releaseDate": "2026-08-05",
    "audience": 838709,
    "boRank": 5,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "언론 보도 (국제뉴스·톱스타뉴스)",
    "sourceUrl": "https://www.gukjenews.com/news/articleView.html?idxno=3658997"
  },
  {
    "id": "tmdb-1545621",
    "tmdbId": 1545621,
    "title": "명탐정 코난: 하이웨이의 타천사",
    "meta": "애니메이션 · 액션 · 미스터리",
    "meta2": "110분",
    "posterPath": "/uvhDoTtOyoUO0hn02buTv2rxyf8.jpg",
    "releaseDate": "2026-08-12",
    "audience": 403090,
    "boRank": 6,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "위치 미확인",
        "len": "",
        "desc": "쿠키 영상이 있습니다. 자세한 내용은 출처를 확인하세요."
      }
    ],
    "tip": "",
    "source": "나무위키",
    "sourceUrl": "https://namu.wiki/w/%EB%AA%85%ED%83%90%EC%A0%95%20%EC%BD%94%EB%82%9C%3A%20%ED%95%98%EC%9D%B4%EC%9B%A8%EC%9D%B4%EC%9D%98%20%ED%83%80%EC%B2%9C%EC%82%AC"
  },
  {
    "id": "tmdb-1307247",
    "tmdbId": 1307247,
    "title": "오케이 마담 2",
    "meta": "액션 · 코미디",
    "meta2": "109분",
    "posterPath": "/xDbrWXB9yb5aEdt4peVy8OWNP2Y.jpg",
    "releaseDate": "2026-08-12",
    "audience": 334907,
    "boRank": 8,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "위치 미확인",
        "len": "",
        "desc": "지훈의 권총에 맞았지만 꿈틀거리며 생존 플래그를 남기더니 쿠키 영상에서 복수를 예고하면서 끝난다."
      }
    ],
    "tip": "",
    "source": "나무위키",
    "sourceUrl": "https://namu.wiki/w/%EC%98%A4%EC%BC%80%EC%9D%B4%20%EB%A7%88%EB%8B%B42"
  },
  {
    "id": "tmdb-1235769",
    "tmdbId": 1235769,
    "title": "경주기행",
    "meta": "드라마 · 미스터리 · 범죄",
    "meta2": "111분",
    "posterPath": "/2dAd2APyFUyJ6qEv9VFHdHQtQI6.jpg",
    "releaseDate": "2026-08-26",
    "audience": 192384,
    "boRank": 3,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키 영상은 확인되지 않았습니다. 다만 엔딩 크레딧에 무술감독 고 박인혜를 추모하는 문구가 들어 있습니다.",
    "source": "언론 보도",
    "sourceUrl": "https://www.mt.co.kr/entertainment/2026/08/26/2026082611537225743"
  },
  {
    "id": "insidious-out-of-the-further",
    "tmdbId": 1291595,
    "title": "인시디어스: 그들이 넘어왔다",
    "meta": "공포 · 스릴러",
    "meta2": "106분",
    "posterPath": "/aKkPEqUtbEtCB5WWJWanHJPFsnZ.jpg",
    "releaseDate": "2026-08-20",
    "audience": 148333,
    "boRank": 7,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "만신창이가 된 사이러스가 치과 의자에 내던져져 결박되는 장면이 나옵니다. 그가 빠져나오려 몸부림치는 사이, 젬마를 습격했던 사악한 치과의사 키페이스가 나타납니다. 키페이스는 붉은 문을 잠근 뒤 사이러스의 앞니를 드릴로 뚫기 시작합니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/08/insidious-out-of-the-further-2026/"
  },
  {
    "id": "the-end-of-oak-street",
    "tmdbId": 1101383,
    "title": "오크 스트리트의 마지막 날",
    "meta": "SF · 미스터리 · 스릴러",
    "meta2": "100분",
    "posterPath": "/oGqJr59UAwZfpmSkEkaW02o0ZLC.jpg",
    "releaseDate": "2026-08-26",
    "audience": 107438,
    "boRank": 4,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/08/end-of-oak-street-the-2026/"
  },
  {
    "id": "paw-patrol-the-dino-movie",
    "tmdbId": 1185806,
    "title": "퍼피 구조대: 더 다이노 무비",
    "meta": "애니메이션 · 모험 · 가족",
    "meta2": "89분",
    "posterPath": "/AnG0YQdnIf3mMYEVc2onMeAROzU.jpg",
    "releaseDate": "2026-08-13",
    "audience": 106540,
    "boRank": 9,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "엔딩 크레딧 앞부분에 애니메이션 장면들이 나옵니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/08/paw-patrol-the-dino-movie-2026/"
  },
  {
    "id": "the-mortuary-assistant",
    "tmdbId": 1470130,
    "title": "모추어리 어시스턴트",
    "meta": "공포 · 미스터리",
    "meta2": "92분",
    "posterPath": "/8ecHzn9eixgpfwZZWorXpCIL5cT.jpg",
    "releaseDate": "2026-08-28",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/02/mortuary-assistant-the-2026/"
  },
  {
    "id": "y-n-lapsi",
    "tmdbId": 964849,
    "title": "나이트본",
    "meta": "공포",
    "meta2": "91분",
    "posterPath": "/8lpzyhJxb1edjfG4ZPKRC2cymHN.jpg",
    "releaseDate": "2026-08-27",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "the-bay",
    "tmdbId": 1430698,
    "title": "블러드 베이: 노 이스케이프",
    "meta": "스릴러 · 공포",
    "meta2": "87분",
    "posterPath": "/hqzxCqbRS6YmYzgTYHW3dsWGoPD.jpg",
    "releaseDate": "2026-08-27",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "the-dog-stars",
    "tmdbId": 1384216,
    "title": "도그 스타: 마지막 희망",
    "meta": "SF · 모험 · 스릴러",
    "meta2": "119분",
    "posterPath": "/cttXvh438Mqp55loQMDofsd4yiC.jpg",
    "releaseDate": "2026-08-26",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/08/dog-stars-the-2026/"
  },
  {
    "id": "dracula",
    "tmdbId": 1246049,
    "title": "드라큘라: 러브 테일",
    "meta": "공포 · 판타지 · 로맨스",
    "meta2": "129분",
    "posterPath": "/3mNCAoWAOHUYaY1VxOCqKC3v8n3.jpg",
    "releaseDate": "2026-08-26",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/02/dracula-2025/"
  },
  {
    "id": "tmdb-1317276",
    "tmdbId": 1317276,
    "title": "극장판 기븐 – 바다로",
    "meta": "애니메이션 · 로맨스",
    "meta2": "81분",
    "posterPath": "/gKdj0W5hUMeIddXFASOs4PdaUJA.jpg",
    "releaseDate": "2026-08-26",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 일본 개봉 당시 주차를 바꿔가며 확인한 관객 후기 기준입니다.",
    "source": "일본 현지 관람 후기",
    "sourceUrl": "https://muko.kr/movietalk/12341784"
  },
  {
    "id": "warfare",
    "tmdbId": 1241436,
    "title": "워페어",
    "meta": "전쟁 · 액션",
    "meta2": "96분",
    "posterPath": "/8GhjvK3T14yx2CVYCeJuUYfMZUI.jpg",
    "releaseDate": "2026-08-19",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2025/04/warfare-2025/"
  },
  {
    "id": "the-wicker-man",
    "tmdbId": 16307,
    "title": "위커 맨: 파이널 컷",
    "meta": "공포",
    "meta2": "93분",
    "posterPath": "/oglvMOKY0ne2Sl3rPC6bHp07EpY.jpg",
    "releaseDate": "2026-08-19",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 1973년 작품이라 쿠키 영상이라는 관습 자체가 없던 시절입니다.",
    "source": "파이널 컷 판본 비교 자료",
    "sourceUrl": "https://twm.fandom.com/wiki/Final_Cut"
  },
  {
    "id": "tmdb-805627",
    "tmdbId": 805627,
    "title": "드로스테 저편의 우리들",
    "meta": "코미디 · SF",
    "meta2": "71분",
    "posterPath": "/i0GXVBO7IjWm4n9VkcpBmp4xEJ5.jpg",
    "releaseDate": "2026-08-19",
    "audience": null,
    "boRank": null,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "크레딧이 올라가는 도중에 쿠키 영상이 나온다."
      }
    ],
    "tip": "",
    "source": "나무위키",
    "sourceUrl": "https://namu.wiki/w/%EB%93%9C%EB%A1%9C%EC%8A%A4%ED%85%8C%20%EC%A0%80%ED%8E%B8%EC%9D%98%20%EC%9A%B0%EB%A6%AC%EB%93%A4"
  },
  {
    "id": "dangerous-animals",
    "tmdbId": 1285965,
    "title": "데인저러스 애니멀스",
    "meta": "공포 · 스릴러",
    "meta2": "99분",
    "posterPath": "/v4mopTpB6QTEF1p6CTKUuoOSL6i.jpg",
    "releaseDate": "2026-08-12",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2025/06/dangerous-animals-2025/"
  },
  {
    "id": "katseye-wild-hearts",
    "tmdbId": 1728113,
    "title": "캣츠아이 - 와일드 하츠",
    "meta": "다큐멘터리 · 음악",
    "meta2": "84분",
    "posterPath": "/qVmnPdA2P3RfRXY2CCSUaSfXxDA.jpg",
    "releaseDate": "2026-08-12",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "jackass-best-and-last",
    "tmdbId": 1612018,
    "title": "잭애스: 베스트 앤드 라스트",
    "meta": "액션 · 코미디 · 다큐멘터리",
    "meta2": "92분",
    "posterPath": "/5xyyeCw2vrOtwJOfk7mApgf2VNU.jpg",
    "releaseDate": "2026-08-06",
    "audience": null,
    "boRank": null,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "크레딧 내내 촬영 종료를 자축하는 멤버들의 모습과 NG 장면, 잭애스 TV·영화 시리즈의 비하인드 영상이 함께 흐릅니다."
      },
      {
        "pos": "크레딧 종료 후",
        "len": "",
        "desc": "원하던 장면을 건졌다며 소감을 말하는 자니의 마지막 클립이 크레딧이 끝난 뒤까지 이어집니다. 몇 초간 검은 화면이 지나가면, 손으로 스프링 도어스토퍼를 여러 번 튕기는 짧은 영상이 나옵니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/06/jackass-best-and-last-2026/"
  }
];

const INITIAL_VOTES = {
  "the-odyssey": {
    "up": 0,
    "down": 0
  },
  "spider-man-brand-new-day": {
    "up": 0,
    "down": 0
  },
  "tmdb-1436168": {
    "up": 0,
    "down": 0
  },
  "tmdb-1545621": {
    "up": 0,
    "down": 0
  },
  "tmdb-1307247": {
    "up": 0,
    "down": 0
  },
  "tmdb-1235769": {
    "up": 0,
    "down": 0
  },
  "insidious-out-of-the-further": {
    "up": 0,
    "down": 0
  },
  "the-end-of-oak-street": {
    "up": 0,
    "down": 0
  },
  "paw-patrol-the-dino-movie": {
    "up": 0,
    "down": 0
  },
  "the-mortuary-assistant": {
    "up": 0,
    "down": 0
  },
  "y-n-lapsi": {
    "up": 0,
    "down": 0
  },
  "the-bay": {
    "up": 0,
    "down": 0
  },
  "the-dog-stars": {
    "up": 0,
    "down": 0
  },
  "dracula": {
    "up": 0,
    "down": 0
  },
  "tmdb-1317276": {
    "up": 0,
    "down": 0
  },
  "warfare": {
    "up": 0,
    "down": 0
  },
  "the-wicker-man": {
    "up": 0,
    "down": 0
  },
  "tmdb-805627": {
    "up": 0,
    "down": 0
  },
  "dangerous-animals": {
    "up": 0,
    "down": 0
  },
  "katseye-wild-hearts": {
    "up": 0,
    "down": 0
  },
  "jackass-best-and-last": {
    "up": 0,
    "down": 0
  }
};
