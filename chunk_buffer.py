from typing import List, Optional

class ChunkBuffer:
    """
    Token tabanlı stream sırasında gelen token'ları
    belirli bir uzunluğa ulaşana kadar geçici olarak tutar
    ve bu uzunluğa ulaşıldığında bir 'chunk' olarak döndürür.
    """

    def __init__(self, chunk_size: int = 50):
        """
        Args:
            chunk_size (int): Chunk başına token sayısı.
                              Örneğin 50 token dolunca chunk döner.
        """
        self.chunk_size = chunk_size
        self._buffer: List[str] = []

    def add_token(self, token: str) -> Optional[str]:
        """
        Yeni gelen bir token'ı buffer'a ekler.
        Eğer buffer dolmuşsa, chunk'ı döndürür.

        Args:
            token (str): LLM'den gelen token.

        Returns:
            Optional[str]: Buffer dolduysa chunk stringi, dolmadıysa None.
        """
        self._buffer.append(token)
        # Buffer dolduysa chunk oluştur ve döndür
        if len(self._buffer) >= self.chunk_size:
            return self.flush()
        return None

    def flush(self) -> Optional[str]:
        """
        Buffer'da kalan token'ları birleştirir ve döndürür.
        Buffer'ı sıfırlar.

        Returns:
            Optional[str]: Mevcut chunk stringi veya None.
        """
        if not self._buffer:
            return None
        chunk = "".join(self._buffer)
        self._buffer.clear()
        return chunk

    def get_buffer_length(self) -> int:
        """Anlık buffer'daki token sayısını döndürür."""
        return len(self._buffer)

    def reset(self):
        """Buffer’ı manuel olarak temizler."""
        self._buffer.clear()
