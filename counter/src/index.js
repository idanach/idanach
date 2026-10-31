// The profile page's visit counter (Idan, 2026-10-31: "can you add a profile view counter? so I know how many people
// visit it", kept private: his answer A). README.md shows an invisible 1 x 1 picture from /github.svg; each time GitHub
// loads it for a visitor (its image proxy asks every time, since the answer says not to keep it), the day's count goes
// up by one. Only page loads are counted, his own and robots' too: GitHub's proxy hides who is asking.
// /stats gives the totals to whoever sends the key (STATS_TOKEN, a secret of this Worker), and nothing to anyone else.
// One Durable Object holds the counts, a row per day in its own SQLite.
import { DurableObject } from "cloudflare:workers";

export class Counter extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    ctx.storage.sql.exec("CREATE TABLE IF NOT EXISTS days (day TEXT PRIMARY KEY, n INTEGER NOT NULL)");
  }

  hit(day) {
    this.ctx.storage.sql.exec("INSERT INTO days (day, n) VALUES (?, 1) ON CONFLICT(day) DO UPDATE SET n = n + 1", day);
  }

  stats() {
    const days = [...this.ctx.storage.sql.exec("SELECT day, n FROM days ORDER BY day DESC LIMIT 90")];
    const total = this.ctx.storage.sql.exec("SELECT COALESCE(SUM(n), 0) AS total FROM days").one().total;
    return { total, days };
  }
}

const PIXEL = '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>';
const FRESH = { "cache-control": "no-cache, no-store, must-revalidate, max-age=0", expires: "0" };

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    const counter = env.COUNTER.get(env.COUNTER.idFromName("github-profile"));
    if (pathname === "/github.svg") {
      await counter.hit(new Date().toISOString().slice(0, 10));
      return new Response(PIXEL, { headers: { "content-type": "image/svg+xml", ...FRESH } });
    }
    if (pathname === "/stats" && env.STATS_TOKEN && request.headers.get("authorization") === "Bearer " + env.STATS_TOKEN) {
      return Response.json(await counter.stats(), { headers: FRESH });
    }
    return new Response("Not found", { status: 404 });
  },
};
