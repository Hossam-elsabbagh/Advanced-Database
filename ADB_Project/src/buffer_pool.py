from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class BufferStep:
    step: int
    page: int
    status: str
    evicted: int | None
    buffer: list[int]
    a1in: list[int]
    am: list[int]
    clock_reference_bits: dict[int, int]
    message: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["clock_reference_bits"] = {str(k): v for k, v in self.clock_reference_bits.items()}
        return data


class BufferPool:
    """Buffer pool simulator supporting LRU, LRU-2, CLOCK, and 2Q policies."""

    VALID_POLICIES = {"LRU", "LRU-2", "CLOCK", "2Q"}

    def __init__(self, size: int, policy: str = "LRU") -> None:
        if size <= 0:
            raise ValueError("Buffer size must be greater than zero.")

        policy = policy.upper().strip()
        if policy not in self.VALID_POLICIES:
            raise ValueError(f"Invalid policy '{policy}'. Choose from {sorted(self.VALID_POLICIES)}.")

        self.size = size
        self.policy = policy
        self.frames: list[int] = []
        self.page_table: dict[int, bool] = {}
        self.time = 0
        self.last_used: dict[int, int] = {}
        self.history: defaultdict[int, list[int]] = defaultdict(list)
        self.clock: list[int] = []
        self.ref_bit: dict[int, int] = {}
        self.clock_hand = 0
        self.a1in: deque[int] = deque()
        self.am: deque[int] = deque()
        self.steps: list[BufferStep] = []
        self.hits = 0
        self.misses = 0

    def fetch_page(self, page_id: int) -> BufferStep:
        self.time += 1
        evicted: int | None = None

        if page_id in self.page_table:
            self.hits += 1
            status = "HIT"
            self._hit(page_id)
            message = f"Page {page_id} already exists in the buffer."
        else:
            self.misses += 1
            status = "MISS"
            if len(self.frames) >= self.size:
                evicted = self.evict()
            self._add_page(page_id)
            message = f"Page {page_id} was loaded into the buffer."
            if evicted is not None:
                message += f" Page {evicted} was evicted using {self.policy}."

        step = BufferStep(
            step=self.time,
            page=page_id,
            status=status,
            evicted=evicted,
            buffer=list(self.frames),
            a1in=list(self.a1in),
            am=list(self.am),
            clock_reference_bits=dict(self.ref_bit),
            message=message,
        )
        self.steps.append(step)
        return step

    def simulate(self, pages: list[int]) -> dict[str, Any]:
        for page in pages:
            self.fetch_page(page)

        total = self.hits + self.misses
        return {
            "policy": self.policy,
            "buffer_size": self.size,
            "pages": pages,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 4) if total else 0,
            "miss_rate": round(self.misses / total, 4) if total else 0,
            "final_buffer": list(self.frames),
            "steps": [step.to_dict() for step in self.steps],
        }

    def _hit(self, page_id: int) -> None:
        self.last_used[page_id] = self.time
        self.history[page_id].append(self.time)

        if self.policy == "LRU":
            self.frames.remove(page_id)
            self.frames.append(page_id)
        elif self.policy == "CLOCK":
            self.ref_bit[page_id] = 1
        elif self.policy == "2Q":
            if page_id in self.a1in:
                self.a1in.remove(page_id)
                self.am.append(page_id)
            elif page_id in self.am:
                self.am.remove(page_id)
                self.am.append(page_id)

    def _add_page(self, page_id: int) -> None:
        self.frames.append(page_id)
        self.page_table[page_id] = True
        self.last_used[page_id] = self.time
        self.history[page_id].append(self.time)

        if self.policy == "CLOCK":
            self.clock.append(page_id)
            self.ref_bit[page_id] = 1
        elif self.policy == "2Q":
            self.a1in.append(page_id)

    def evict(self) -> int:
        if self.policy == "LRU":
            victim = min(self.frames, key=lambda p: self.last_used[p])
        elif self.policy == "LRU-2":
            victim = self._evict_lru2()
        elif self.policy == "CLOCK":
            victim = self._evict_clock()
        elif self.policy == "2Q":
            victim = self._evict_2q()
        else:
            raise ValueError("Invalid policy.")

        self._remove_page(victim)
        return victim

    def _remove_page(self, page_id: int) -> None:
        self.frames.remove(page_id)
        del self.page_table[page_id]
        self.last_used.pop(page_id, None)
        self.history.pop(page_id, None)

        if self.policy == "CLOCK":
            if page_id in self.clock:
                index = self.clock.index(page_id)
                self.clock.remove(page_id)
                if self.clock:
                    if index < self.clock_hand:
                        self.clock_hand -= 1
                    self.clock_hand %= len(self.clock)
                else:
                    self.clock_hand = 0
            self.ref_bit.pop(page_id, None)
        elif self.policy == "2Q":
            if page_id in self.a1in:
                self.a1in.remove(page_id)
            if page_id in self.am:
                self.am.remove(page_id)

    def _evict_lru2(self) -> int:
        candidates: list[tuple[int, int, int]] = []
        for page in self.frames:
            accesses = self.history[page]
            if len(accesses) < 2:
                kth_access = accesses[0]
                priority_group = 0
            else:
                kth_access = accesses[-2]
                priority_group = 1
            candidates.append((priority_group, kth_access, page))
        candidates.sort()
        return candidates[0][2]

    def _evict_clock(self) -> int:
        while True:
            if not self.clock:
                raise RuntimeError("CLOCK list is empty.")
            self.clock_hand %= len(self.clock)
            page = self.clock[self.clock_hand]
            if self.ref_bit[page] == 0:
                return page
            self.ref_bit[page] = 0
            self.clock_hand = (self.clock_hand + 1) % len(self.clock)

    def _evict_2q(self) -> int:
        if self.a1in:
            return self.a1in[0]
        if self.am:
            return self.am[0]
        raise RuntimeError("2Q queues are empty.")


def parse_page_sequence(text: str) -> list[int]:
    if not text or not text.strip():
        raise ValueError("Enter at least one page number.")
    parts = text.replace("\n", ",").replace(";", ",").split(",")
    pages: list[int] = []
    for part in parts:
        stripped = part.strip()
        if not stripped:
            continue
        try:
            pages.append(int(stripped))
        except ValueError as exc:
            raise ValueError(f"Invalid page number: {stripped}") from exc
    if not pages:
        raise ValueError("Enter at least one page number.")
    return pages
