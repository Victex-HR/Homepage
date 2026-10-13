// 공개 페이지의 '갱신' 버튼이 부르는 함수.
// 나라장터(공공데이터포털) 입찰공고를 since 이후부터 지금까지 바로 받아 돌려준다.
// 인증키는 함수 비밀값 NARA_API_KEY 에만 두고 브라우저에는 내보내지 않는다.

const API_URL = "https://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo";
const PAGE_SIZE = 100;
const SLIM = ["bidNtceNo", "bidNtceOrd", "bidNtceNm", "bidNtceSttusNm", "bidNtceDate", "bidNtceBgn",
  "bsnsDivNm", "cntrctCnclsMthdNm", "bidwinrDcsnMthdNm", "ntceInsttNm", "dmndInsttNm",
  "bidPrtcptQlfctRgstClseDate", "bidPrtcptQlfctRgstClseTm", "bidClseDate", "bidClseTm",
  "opengDate", "opengTm", "asignBdgtAmt", "presmptPrce", "rgnLmtYn", "prtcptPsblRgnNm",
  "indstrytyLmtYn", "bidprcPsblIndstrytyNm", "bidNtceUrl"];
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};
const CACHE_MS = 3 * 60 * 1000;   // 여러 사람이 연달아 눌러도 같은 시간대는 3분 동안 다시 묻지 않음
const cache = new Map<string, { at: number; items: Record<string, string>[] }>();

const pad = (n: number) => String(n).padStart(2, "0");
// 한국 시각 기준 Date (UTC 필드에 KST 값을 담아 씀)
const kstNow = () => new Date(Date.now() + 9 * 3600e3);
const ymd = (d: Date) => `${d.getUTCFullYear()}${pad(d.getUTCMonth() + 1)}${pad(d.getUTCDate())}`;

async function fetchPage(key: string, begin: string, end: string, page: number) {
  const q = new URLSearchParams({ ServiceKey: key, numOfRows: String(PAGE_SIZE), pageNo: String(page),
    type: "json", bidNtceBgnDt: begin, bidNtceEndDt: end });
  let last = "";
  for (let attempt = 0; attempt < 4; attempt++) {
    try {
      const r = await fetch(`${API_URL}?${q}`, { signal: AbortSignal.timeout(20000) });
      const data = await r.json();
      const resp = data.response ?? data, hdr = resp.header ?? {};
      if (!["00", "0"].includes(String(hdr.resultCode ?? "00"))) throw new Error(`API 오류 ${hdr.resultCode}: ${hdr.resultMsg}`);
      const body = resp.body ?? {};
      let items = body.items ?? [];
      if (!Array.isArray(items)) items = items.item ?? [];
      if (!Array.isArray(items)) items = [items];
      return { items, total: +(body.totalCount || 0) };
    } catch (e) {
      last = String(e);
      await new Promise((ok) => setTimeout(ok, 1500 * (attempt + 1)));
    }
  }
  throw new Error(last);
}

// 한 시간대 공고를 모두 받는다. 페이지 순서가 흔들려 빠지는 건이 있으면 한 번 더 받아 합친다.
async function fetchWindow(key: string, begin: string, end: string, isCurrent: boolean) {
  const hit = cache.get(begin);
  if (hit && (!isCurrent || Date.now() - hit.at < CACHE_MS)) return hit.items;
  const got = new Map<string, Record<string, string>>();
  for (let round = 0; round < 3; round++) {
    const first = await fetchPage(key, begin, end, 1);
    const pages = Math.ceil(first.total / PAGE_SIZE);
    const rest = await Promise.all(Array.from({ length: Math.max(0, pages - 1) }, (_, i) => fetchPage(key, begin, end, i + 2)));
    for (const it of [first, ...rest].flatMap((p) => p.items)) got.set(`${it.bidNtceNo}-${it.bidNtceOrd}`, it);
    if (got.size >= first.total) break;
  }
  const items = [...got.values()].map((r) => Object.fromEntries(SLIM.map((f) => [f, r[f] == null ? "" : String(r[f])])));
  cache.set(begin, { at: Date.now(), items });
  return items;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  const json = (body: unknown, status = 200) =>
    new Response(JSON.stringify(body), { status, headers: { ...CORS, "Content-Type": "application/json; charset=utf-8" } });
  const key = Deno.env.get("NARA_API_KEY");
  if (!key) return json({ error: "함수 비밀값 NARA_API_KEY 가 없습니다." }, 500);

  // since: 이미 가진 가장 최근 공고 시각 'YYYY-MM-DD HH:MM'. 없거나 오늘보다 앞이면 오늘 0시부터.
  const now = kstNow(), today = ymd(now);
  const m = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2})/.exec(new URL(req.url).searchParams.get("since") ?? "");
  let fromHour = 0;
  if (m && `${m[1]}${m[2]}${m[3]}` === today) fromHour = +m[4];
  const toHour = now.getUTCHours();

  try {
    const hours = Array.from({ length: toHour - fromHour + 1 }, (_, i) => fromHour + i);
    const lists = await Promise.all(hours.map((h) =>
      fetchWindow(key, `${today}${pad(h)}00`, `${today}${pad(h)}59`, h >= toHour - 1)));
    const items = lists.flat().sort((a, b) => (a.bidNtceBgn || "").localeCompare(b.bidNtceBgn || ""));
    return json({
      fetched_at: `${now.toISOString().slice(0, 10)} ${pad(now.getUTCHours())}:${pad(now.getUTCMinutes())}`,
      date: `${today.slice(0, 4)}-${today.slice(4, 6)}-${today.slice(6)}`,
      from_hour: fromHour, items,
    });
  } catch (e) {
    return json({ error: `나라장터 조회 실패: ${e}` }, 502);
  }
});
