from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.logger import logger
from app.schema import Memory as BaseMemory, Message


class ValidatedMemory(BaseMemory):
    """유효성 검사가 추가된 메모리 클래스"""
    
    def add_message(self, message: Message) -> None:
        """메시지를 추가하기 전에 유효성 검사"""
        # tool 메시지인 경우 이전에 해당 tool_call_id와 일치하는 assistant 메시지가 있는지 확인
        if message.role == "tool" and message.tool_call_id:
            self._validate_tool_message(message)
            
        # 메시지 추가
        super().add_message(message)
    
    def _validate_tool_message(self, message: Message) -> None:
        """tool 메시지가 유효한지 검사"""
        if not message.tool_call_id:
            logger.warning(f"Tool 메시지에 tool_call_id가 없습니다: {message}")
            return
            
        # 이전 메시지에서 일치하는 tool_call_id를 가진 assistant 메시지 찾기
        found_matching_call = False
        for prev_msg in reversed(self.messages):  # 가장 최근 메시지부터 검색
            if prev_msg.role == "assistant" and prev_msg.tool_calls:
                for tool_call in prev_msg.tool_calls:
                    if isinstance(tool_call, dict) and tool_call.get("id") == message.tool_call_id:
                        found_matching_call = True
                        break
                if found_matching_call:
                    break
        
        if not found_matching_call:
            logger.warning(
                f"Tool 메시지 {message.tool_call_id}에 일치하는 assistant 메시지의 tool_call을 찾을 수 없습니다. "
                "OpenAI API는 'tool' 역할 메시지가 'tool_calls'가 있는 메시지 다음에 와야 합니다."
            )
    
    def add_messages(self, messages: List[Message]) -> None:
        """여러 메시지를 추가할 때 개별적으로 유효성 검사"""
        for message in messages:
            self.add_message(message)
            
    @classmethod
    def from_base_memory(cls, memory: BaseMemory) -> "ValidatedMemory":
        """기존 Memory 객체로부터 ValidatedMemory 생성"""
        return cls(messages=memory.messages, max_messages=memory.max_messages) 