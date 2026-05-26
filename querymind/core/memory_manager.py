"""Thread-safe, per-session conversation memory management.

Wraps LangChain's :class:`ConversationBufferWindowMemory` to provide
isolated conversation histories for each user session, exposed through
a singleton :data:`memory_manager` instance.
"""

from __future__ import annotations

import threading
from typing import Final

from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class MemoryManager:
    """Manages per-session conversation memory using a sliding window.

    Each session maintains the last *k* interaction turns (default 10).
    All access to the internal session dictionary is guarded by a
    :class:`threading.Lock` to ensure thread safety when the manager is
    shared across async tasks or worker threads.
    """

    _DEFAULT_WINDOW_SIZE: Final[int] = 10

    def __init__(self) -> None:
        """Initialise the memory manager with an empty session store."""
        self._sessions: dict[str, ConversationBufferWindowMemory] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Session access
    # ------------------------------------------------------------------

    def get_memory(self, session_id: str) -> ConversationBufferWindowMemory:
        """Return the memory buffer for *session_id*, creating one if needed.

        Parameters
        ----------
        session_id:
            A unique identifier for the conversation session.

        Returns
        -------
        ConversationBufferWindowMemory
            The conversation memory instance for the session.
        """
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = ConversationBufferWindowMemory(
                    k=self._DEFAULT_WINDOW_SIZE,
                    return_messages=True,
                    memory_key="chat_history",
                )
            return self._sessions[session_id]

    # ------------------------------------------------------------------
    # Interaction recording
    # ------------------------------------------------------------------

    def add_interaction(self, session_id: str, user_input: str, ai_output: str) -> None:
        """Record a single user/AI interaction turn.

        Parameters
        ----------
        session_id:
            The session to append the turn to.
        user_input:
            The human message text.
        ai_output:
            The AI assistant response text.
        """
        memory = self.get_memory(session_id)
        memory.save_context(
            {"input": user_input},
            {"output": ai_output},
        )

    # ------------------------------------------------------------------
    # History retrieval
    # ------------------------------------------------------------------

    def get_history(self, session_id: str) -> list[BaseMessage]:
        """Return the message history for *session_id*.

        Parameters
        ----------
        session_id:
            The session whose history to retrieve.

        Returns
        -------
        list[BaseMessage]
            Ordered list of :class:`HumanMessage` and :class:`AIMessage`
            objects.  Returns an empty list if the session does not exist.
        """
        with self._lock:
            if session_id not in self._sessions:
                return []
            memory = self._sessions[session_id]

        # load_memory_variables returns {"chat_history": [messages...]}
        variables = memory.load_memory_variables({})
        return variables.get("chat_history", [])

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def clear_session(self, session_id: str) -> None:
        """Delete all memory for *session_id*.

        Parameters
        ----------
        session_id:
            The session to remove.  No-op if it does not exist.
        """
        with self._lock:
            self._sessions.pop(session_id, None)

    def active_sessions(self) -> list[str]:
        """Return a list of all session IDs that currently have memory.

        Returns
        -------
        list[str]
            Session identifiers with active conversation buffers.
        """
        with self._lock:
            return list(self._sessions.keys())


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
memory_manager: Final[MemoryManager] = MemoryManager()
