# Frozen judge request construction

Documentation excerpt; no inference client is released. Rubric and system prompt are in the adjacent materials.

```python
def _system(self) -> list[dict]:
        return [{"type": "text", "text": self.prompt + "\n\n---\n\n" + self.rubric, "cache_control": {"type": "ephemeral"}}]

def _hidden_profile_text(record: dict) -> str:
        p = (record.get("persona") or {}).get("hidden_profile")
        if not p:
            return "(없음 — 회귀 프로브 세션)"
        return (f"정답 직무: {', '.join(p.get('suitable_jobs', []))}\n제약: {', '.join(p.get('constraints', []))}\n"
                f"끌어내야 할 사실(key_facts): " + " | ".join(p.get("key_facts", [])))

def _user_block(self, record: dict, programmatic: V.ProgrammaticVerdict | None = None) -> str:
        parts = [f"[BRANCH]\n{record.get('branch')}",
                 f"[HIDDEN_PROFILE]\n{self._hidden_profile_text(record)}",
                 f"[TOOL_LOG]\n{tool_log_text(record) or '(도구 호출 없음)'}",
                 f"[SESSION_TRANSCRIPT]\n{transcript_text(record)}"]
        if programmatic is not None:
            det = {k: v for k, v in programmatic.details.items() if k not in ("f7_noncanonical", "f5_repeat_flag", "max_consecutive_jaccard", "max_self_repeat")}
            parts.append("[PROGRAMMATIC_VERDICT — 코드 판정(F1/F4/F6), 오버라이드 불가]\n"
                         f"F1={programmatic.F1} F4={programmatic.F4} F6={programmatic.F6} 세부: {det}\n"
                         "(F5 반복 성분·F7 직업명 성분은 코드가 별도로 판정해 나중에 합칩니다. 당신의 F5/F7 필드에는 잔여 판정만 적으세요.)")
        return "\n\n".join(parts)

def build_session_request(self, record: dict, custom_id: str | None = None) -> dict:
        prog = V.verify_session(record)
        params = {"model": self.model, "max_tokens": JUDGE_MAX_TOKENS, "system": self._system(),
                  "tools": [SUBMIT_TOOL], "tool_choice": {"type": "tool", "name": "submit_verdict"},
                  "messages": [{"role": "user", "content": self._user_block(record, prog)}]}
        return {"custom_id": custom_id or f"sess:{record.get('session_id')}:{self.model}", "params": params}

def build_turn_request(self, record: dict, custom_id: str | None = None) -> dict:
        params = {"model": self.model, "max_tokens": JUDGE_MAX_TOKENS, "system": self._system(),
                  "tools": [SUBMIT_TURNS_TOOL], "tool_choice": {"type": "tool", "name": "submit_turn_verdicts"},
                  "messages": [{"role": "user", "content": self._user_block(record) +
                                "\n\n각 상담사 턴(0부터, 상담사 발화만 셈)에 대해 F1~F7 실패 여부를 판정하세요."}]}
        return {"custom_id": custom_id or f"turns:{record.get('session_id')}:{self.model}", "params": params}

def build_pairwise_request(self, rec_a: dict, rec_b: dict, custom_id: str, rng: random.Random | None = None) -> tuple[dict, bool]:
        """(요청, swapped). swapped=True 면 모델이 본 A 는 rec_b 였다."""
        rng = rng or random
        swapped = rng.random() < 0.5
        first, second = (rec_b, rec_a) if swapped else (rec_a, rec_b)
        content = (f"[BRANCH]\n{rec_a.get('branch')}\n\n[HIDDEN_PROFILE]\n{self._hidden_profile_text(rec_a)}\n\n"
                   f"[SESSION A]\n{transcript_text(first)}\n\n[TOOL_LOG A]\n{tool_log_text(first, 3000) or '(없음)'}\n\n"
                   f"[SESSION B]\n{transcript_text(second)}\n\n[TOOL_LOG B]\n{tool_log_text(second, 3000) or '(없음)'}\n\n"
                   "같은 시나리오의 두 세션입니다. 루브릭 기준(규칙 위반·내담자 효용)으로 더 나은 세션을 고르세요. "
                   "길이·문체에 가점을 주지 마세요. 동등하면 tie.")
        params = {"model": self.model, "max_tokens": 1500, "system": self._system(),
                  "tools": [SUBMIT_PAIR_TOOL], "tool_choice": {"type": "tool", "name": "submit_pairwise"},
                  "messages": [{"role": "user", "content": content}]}
        return {"custom_id": custom_id, "params": params}, swapped
```
