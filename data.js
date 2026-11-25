/* 쿠키이써 — 현재 상영작.
   자동 생성 파일입니다. 직접 고치지 말고 `python3 tools/fetch_movies.py` 를 실행하세요.
   작품 정보: TMDB /movie/now_playing?region=KR (조회일 2026-11-25)
   관객수: KOBIS 일별 박스오피스 (기준일 20261124)
   쿠키 정보: aftercredits.com + 나무위키 + 자동 조사 + TMDB 키워드 + data.overrides.json */

const DATA_UPDATED = '2026-11-25';
const BOXOFFICE_DATE = "20261124";

const MOVIES = [
  {
    "id": "la-la-land",
    "tmdbId": 313369,
    "title": "라라랜드",
    "meta": "코미디 · 드라마 · 로맨스",
    "meta2": "127분",
    "posterPath": "/ad9ndytwOckyShSc0A6tx1rZRkW.jpg",
    "releaseDate": "2016-12-07",
    "audience": 3910121,
    "boRank": 6,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com (자동 조사)",
    "sourceUrl": "https://aftercredits.com/2016/12/la-la-land-2016/"
  },
  {
    "id": "tmdb-1586876",
    "tmdbId": 1586876,
    "title": "극장판 치이카와: 인어 섬의 비밀",
    "meta": "애니메이션 · 가족 · 모험",
    "meta2": "99분",
    "posterPath": "/5TMyytCI5Pfc9c1eNsljiCdiB05.jpg",
    "releaseDate": "2026-09-30",
    "audience": 3081238,
    "boRank": 3,
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
    "id": "tmdb-1244809",
    "tmdbId": 1244809,
    "title": "폭설",
    "meta": "스릴러 · 미스터리 · 드라마",
    "meta2": "89분",
    "posterPath": "/xiBYIFWBrLD7Z7jWrt0e7YLLmfC.jpg",
    "releaseDate": "2026-11-18",
    "audience": 499714,
    "boRank": 1,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "ggilbo.com (자동 조사)",
    "sourceUrl": "https://www.ggilbo.com/news/articleView.html?idxno=1193922"
  },
  {
    "id": "heart-of-the-beast",
    "tmdbId": 1263337,
    "title": "하트 오브 비스트",
    "meta": "모험 · 스릴러",
    "meta2": "102분",
    "posterPath": "/zC4E522V1n3H4SGdYOaiqhF5DnS.jpg",
    "releaseDate": "2026-10-28",
    "audience": 476795,
    "boRank": 9,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/09/heart-of-the-beast-2026/"
  },
  {
    "id": "tmdb-1545057",
    "tmdbId": 1545057,
    "title": "최종면접",
    "meta": "미스터리",
    "meta2": "108분",
    "posterPath": "/wImwvRmbR28hPNDmaj5W7zvxk0T.jpg",
    "releaseDate": "2026-11-04",
    "audience": 330291,
    "boRank": 8,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "desc": "본편 외에 쿠키영상이 따로 마련돼 있다고 보도됐다. 영상의 내용과 크레딧 중간인지 종료 후인지는 확인하지 못했다.",
        "len": "",
        "pos": "위치 미확인"
      }
    ],
    "tip": "",
    "source": "etoday.co.kr (자동 조사)",
    "sourceUrl": "https://www.etoday.co.kr/news/view/2642935"
  },
  {
    "id": "fall-2-deadpoint",
    "tmdbId": 1101412,
    "title": "폴2: 데드포인트",
    "meta": "스릴러",
    "meta2": "99분",
    "posterPath": "/9fhPxF6clLRoQfpmgn5jGpL6BTA.jpg",
    "releaseDate": "2026-11-11",
    "audience": 251694,
    "boRank": 4,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/09/fall-2-deadpoint-2026/"
  },
  {
    "id": "tmdb-1777750",
    "tmdbId": 1777750,
    "title": "명탐정 코난: 30호 살인 사건",
    "meta": "애니메이션 · 액션 · 미스터리",
    "meta2": "94분",
    "posterPath": "/8VIxElJnoGXJH4p3Av2BQwgcxpC.jpg",
    "releaseDate": "2026-11-05",
    "audience": 202979,
    "boRank": 10,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "desc": "엔딩 크레디트가 끝난 뒤 쿠키 영상이 1개 나온다. 기사 두 건 모두 장면의 내용은 적지 않았다.",
        "len": "",
        "pos": "크레딧 종료 후"
      }
    ],
    "tip": "",
    "source": "ggilbo.com · topstarnews.net (자동 조사)",
    "sourceUrl": "https://www.ggilbo.com/news/articleView.html?idxno=1190372"
  },
  {
    "id": "the-hunger-games-sunrise-on-the",
    "tmdbId": 1300968,
    "title": "헝거게임 50번째 추첨의 날",
    "meta": "SF · 액션 · 모험",
    "meta2": "159분",
    "posterPath": "/6ehDHRVDtwe1oMu6EMtKC3SoVER.jpg",
    "releaseDate": "2026-11-18",
    "audience": 107500,
    "boRank": 2,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/11/hunger-games-sunrise-on-the-reaping-the-2026/"
  },
  {
    "id": "tmdb-1410955",
    "tmdbId": 1410955,
    "title": "아름다운 초저녁달",
    "meta": "로맨스 · 드라마",
    "meta2": "119분",
    "posterPath": "/qb1ExMXRfo1hvZT691C8zfaFQ3r.jpg",
    "releaseDate": "2026-11-18",
    "audience": 18569,
    "boRank": 7,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "desc": "엔딩 크레딧이 모두 끝난 뒤에 쿠키 영상이 이어진다. 구체적인 내용은 확인하지 못했다.",
        "len": "",
        "pos": "크레딧 종료 후"
      }
    ],
    "tip": "",
    "source": "topstarnews.net · srtimes.kr (자동 조사)",
    "sourceUrl": "https://www.topstarnews.net/news/articleView.html?idxno=16280520"
  },
  {
    "id": "hexed",
    "tmdbId": 1538497,
    "title": "헥스: 마녀왕국",
    "meta": "모험 · 애니메이션 · 가족",
    "meta2": "110분",
    "posterPath": "/rgnSY4Yz3tm8gutVedML3d8UYWy.jpg",
    "releaseDate": "2026-11-25",
    "audience": null,
    "boRank": null,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "빌리와 앨리스가 기다리는 동안, 어리둥절한 계산원이 고양이 피규어 여러 개를 스캔하는 장면이 나옵니다. 계산원은 마지막 피규어를 든 채 봉투가 필요한지 묻습니다. 비프 로저 크럼척이 피규어를 낚아채며 괜찮다고, 자기가 직접 가져왔다고 말합니다. 빌리가 계산원에게 현금을 건네는 사이, 크럼척은 물건이 가득 찬 주전자 안으로 뛰어듭니다. 주전자는 유리문을 부수며 가게 밖으로 미끄러지듯 나갑니다. 빌리는 마법을 써서 계산원의 손에 있는 돈을 불려 파손된 문의 값을 치릅니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/11/hexed-2026/"
  },
  {
    "id": "focker-in-law",
    "tmdbId": 1400336,
    "title": "미트 페어런츠 4",
    "meta": "코미디 · 로맨스",
    "meta2": "106분",
    "posterPath": "/2IfBmpzSuHzjThm2RxgYjIRCU11.jpg",
    "releaseDate": "2026-11-25",
    "audience": null,
    "boRank": null,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "엔딩 크레딧이 올라가는 도중에 에두아르도(도도)가 거짓말 탐지기 테스트를 받는 장면이 나온다. 두 리뷰가 이 장면을 영화에서 가장 웃긴 대목 중 하나로 꼽았다."
      }
    ],
    "tip": "",
    "source": "sacredwall.com · clutchpoints.com (자동 조사)",
    "sourceUrl": "https://www.sacredwall.com/focker-in-law-review/"
  },
  {
    "id": "lilo-scratch",
    "tmdbId": 1720486,
    "title": "Lilo & Scratch",
    "meta": "애니메이션 · 코미디 · 가족",
    "meta2": "",
    "posterPath": "/tbGwR0B0HDPTwX9BbQEIuIHDk3z.jpg",
    "releaseDate": "2026-11-25",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "la-bataille-de-gaulle-j-cris-ton",
    "tmdbId": 1165369,
    "title": "드골2: 자유의 시대",
    "meta": "드라마 · 전쟁 · 역사",
    "meta2": "160분",
    "posterPath": "/3wxvG7GIs3PTExEjhF4fvB0KbBO.jpg",
    "releaseDate": "2026-11-25",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "the-death-of-robin-hood",
    "tmdbId": 1284465,
    "title": "데스 오브 로빈 후드",
    "meta": "모험 · 드라마 · 액션",
    "meta2": "123분",
    "posterPath": "/a1PxMgPpqIXdtq8HEqoPY3zuUAQ.jpg",
    "releaseDate": "2026-11-19",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/06/death-of-robin-hood-the-2026/"
  },
  {
    "id": "other-mommy",
    "tmdbId": 1400837,
    "title": "아더 마미",
    "meta": "공포",
    "meta2": "93분",
    "posterPath": "/2wlzy9T4jsaFAqUtPQNwBj41DYN.jpg",
    "releaseDate": "2026-11-18",
    "audience": null,
    "boRank": null,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 종료 후",
        "len": "",
        "desc": "벨 담(다른 엄마)이 카메라를 내려다보며 입술에 손가락을 갖다 대고 \"쉬이이이잇\" 하고 말합니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/10/other-mommy-2026/"
  },
  {
    "id": "mutiny",
    "tmdbId": 1288445,
    "title": "뮤티니",
    "meta": "액션 · 스릴러",
    "meta2": "95분",
    "posterPath": "/qTXUI63I9pbsZbBRvn1gIXIcwKQ.jpg",
    "releaseDate": "2026-11-12",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/08/mutiny-2026/"
  },
  {
    "id": "ebenezer",
    "tmdbId": 1567605,
    "title": "스크루지: 크리스마스 캐럴",
    "meta": "판타지 · 코미디",
    "meta2": "116분",
    "posterPath": "/mgWk3zPFLKisvKNtJGf6zxDX5gA.jpg",
    "releaseDate": "2026-11-11",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/11/ebenezer-2026/"
  },
  {
    "id": "pressure",
    "tmdbId": 1318413,
    "title": "프레셔",
    "meta": "스릴러 · 역사 · 전쟁",
    "meta2": "100분",
    "posterPath": "/uwqjK4bKEWLfdJX2Oc7odnChH7Y.jpg",
    "releaseDate": "2026-11-11",
    "audience": null,
    "boRank": null,
    "status": "no",
    "creditsLen": null,
    "cookies": [],
    "tip": "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다.",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/05/pressure-2026/"
  },
  {
    "id": "la-bataille-de-gaulle-l-ge-de-fe",
    "tmdbId": 1165366,
    "title": "드골: 저항의 시작",
    "meta": "역사 · 드라마 · 전쟁",
    "meta2": "160분",
    "posterPath": "/jIQoQrDSoBtxmLsymBsmElJqHOL.jpg",
    "releaseDate": "2026-11-11",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "mother-mary",
    "tmdbId": 1102883,
    "title": "마더 메리",
    "meta": "음악 · 스릴러 · 드라마",
    "meta2": "113분",
    "posterPath": "/h1OiG9wLxJPzDa8GtomZ7D5d9H1.jpg",
    "releaseDate": "2026-11-11",
    "audience": null,
    "boRank": null,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "엔딩 크레딧의 앞부분에서는 무대 위에서 마더 메리가 노래 \"Dark Cradle\"을 부르는 장면이 흐릅니다. 크레딧 후반부에는 붉은 드레스와 스케치북이 담긴 영상이 나옵니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/04/mother-mary-2026/"
  },
  {
    "id": "the-virgin-suicides",
    "tmdbId": 1443,
    "title": "처녀 자살 소동",
    "meta": "드라마 · 로맨스",
    "meta2": "97분",
    "posterPath": "/bxEuunUExRCGtDqTQguuZekFTwy.jpg",
    "releaseDate": "2026-11-11",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "tmdb-31347",
    "tmdbId": 31347,
    "title": "극장판 카드캡터 체리 : 봉인된 카드",
    "meta": "애니메이션 · 모험 · 판타지",
    "meta2": "93분",
    "posterPath": "/ezYcCER756g37B4Y7kZKfr2flgc.jpg",
    "releaseDate": "2026-11-11",
    "audience": null,
    "boRank": null,
    "status": "unknown",
    "creditsLen": null,
    "cookies": [],
    "tip": "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요.",
    "source": ""
  },
  {
    "id": "the-cat-in-the-hat",
    "tmdbId": 1117898,
    "title": "모자 쓴 고양이",
    "meta": "애니메이션 · 판타지 · 모험",
    "meta2": "107분",
    "posterPath": "/lgLg6T1kv7fjfANRNM1QSvPKDJM.jpg",
    "releaseDate": "2026-11-06",
    "audience": null,
    "boRank": null,
    "status": "yes",
    "creditsLen": null,
    "cookies": [
      {
        "pos": "크레딧 중간",
        "len": "",
        "desc": "Pig in a Wig의 생일이라 Cat in the Hat이 그에게 Thing들이 든 상자를 선물합니다. 상자가 갑자기 터지듯 열리면서 방 안이 Thing들로 가득 차고, 사무실에서 큰 파티가 벌어집니다.\n이어서 닥터 수스(시어도어 가이젤)의 사진과 함께 다음과 같은 헌정 문구가 나옵니다.\n테오도르 가이젤과 천재의 해에 바칩니다\n크레딧이 계속 올라가는 동안 Cat in the Hat 노래가 흘러나오고, Cat in the Hat이 관객에게 그 노래에 대해 이야기하며 속편과 스핀오프 제작을 제안합니다."
      },
      {
        "pos": "크레딧 종료 후",
        "len": "",
        "desc": "Go-Backer가 화면에 나타납니다. 이 장치가 작동하면서 영화가 처음으로 되감기고 워너 브라더스 로고가 나옵니다. 로고가 뒤집히며 열리고 Cat in the Hat의 실루엣이 나타나 \"다시 한번 해보자!\"라고 외칩니다. 그가 노래를 시작하려고 박자를 세는 순간 인사팀의 셰리가 나타나 영화는 끝났다고 말하고, 로고는 쾅 하고 닫힙니다."
      }
    ],
    "tip": "",
    "source": "aftercredits.com",
    "sourceUrl": "https://aftercredits.com/2026/11/cat-in-the-hat-the-2026/"
  }
];

const INITIAL_VOTES = {
  "la-la-land": {
    "up": 0,
    "down": 0
  },
  "tmdb-1586876": {
    "up": 0,
    "down": 0
  },
  "tmdb-1244809": {
    "up": 0,
    "down": 0
  },
  "heart-of-the-beast": {
    "up": 0,
    "down": 0
  },
  "tmdb-1545057": {
    "up": 0,
    "down": 0
  },
  "fall-2-deadpoint": {
    "up": 0,
    "down": 0
  },
  "tmdb-1777750": {
    "up": 0,
    "down": 0
  },
  "the-hunger-games-sunrise-on-the": {
    "up": 0,
    "down": 0
  },
  "tmdb-1410955": {
    "up": 0,
    "down": 0
  },
  "hexed": {
    "up": 0,
    "down": 0
  },
  "focker-in-law": {
    "up": 0,
    "down": 0
  },
  "lilo-scratch": {
    "up": 0,
    "down": 0
  },
  "la-bataille-de-gaulle-j-cris-ton": {
    "up": 0,
    "down": 0
  },
  "the-death-of-robin-hood": {
    "up": 0,
    "down": 0
  },
  "other-mommy": {
    "up": 0,
    "down": 0
  },
  "mutiny": {
    "up": 0,
    "down": 0
  },
  "ebenezer": {
    "up": 0,
    "down": 0
  },
  "pressure": {
    "up": 0,
    "down": 0
  },
  "la-bataille-de-gaulle-l-ge-de-fe": {
    "up": 0,
    "down": 0
  },
  "mother-mary": {
    "up": 0,
    "down": 0
  },
  "the-virgin-suicides": {
    "up": 0,
    "down": 0
  },
  "tmdb-31347": {
    "up": 0,
    "down": 0
  },
  "the-cat-in-the-hat": {
    "up": 0,
    "down": 0
  }
};
