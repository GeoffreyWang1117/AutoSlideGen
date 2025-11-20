"""
RAG (Retrieval-Augmented Generation) module.
Enhances presentation generation with knowledge base retrieval.
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentStore:
    """Simple document store for RAG."""

    def __init__(self, documents_dir: Optional[str] = None):
        """
        Initialize document store.

        Args:
            documents_dir: Directory containing documents
        """
        if documents_dir is None:
            documents_dir = "./knowledge_base"

        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.documents: List[Dict[str, Any]] = []
        self._load_documents()

    def _load_documents(self):
        """Load documents from directory."""
        supported_extensions = ['.txt', '.md']

        for doc_file in self.documents_dir.rglob('*'):
            if doc_file.suffix in supported_extensions:
                try:
                    content = doc_file.read_text(encoding='utf-8')
                    self.documents.append({
                        'path': str(doc_file),
                        'name': doc_file.name,
                        'content': content,
                        'metadata': {
                            'type': doc_file.suffix[1:],
                            'size': len(content)
                        }
                    })
                except Exception as e:
                    self.logger.error(f"Failed to load document {doc_file}: {e}")

        self.logger.info(f"Loaded {len(self.documents)} documents")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Simple keyword-based search.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant documents
        """
        query_lower = query.lower()
        results = []

        for doc in self.documents:
            content_lower = doc['content'].lower()

            # Simple scoring based on keyword occurrence
            score = content_lower.count(query_lower)

            if score > 0:
                results.append({
                    **doc,
                    'score': score
                })

        # Sort by score and return top k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def add_document(
        self,
        content: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a document to the store.

        Args:
            content: Document content
            name: Document name
            metadata: Optional metadata
        """
        doc_path = self.documents_dir / name

        try:
            doc_path.write_text(content, encoding='utf-8')

            self.documents.append({
                'path': str(doc_path),
                'name': name,
                'content': content,
                'metadata': metadata or {}
            })

            self.logger.info(f"Added document: {name}")

        except Exception as e:
            self.logger.error(f"Failed to add document: {e}")


class RAGEnhancer:
    """RAG-enhanced outline generator."""

    def __init__(
        self,
        llm_generator,
        document_store: Optional[DocumentStore] = None
    ):
        """
        Initialize RAG enhancer.

        Args:
            llm_generator: LLM generator instance
            document_store: Document store (creates new if None)
        """
        self.llm_generator = llm_generator
        self.document_store = document_store or DocumentStore()
        self.logger = logging.getLogger(self.__class__.__name__)

    def retrieve_context(
        self,
        topic: str,
        max_docs: int = 3
    ) -> str:
        """
        Retrieve relevant context from knowledge base.

        Args:
            topic: Presentation topic
            max_docs: Maximum documents to retrieve

        Returns:
            Combined context string
        """
        results = self.document_store.search(topic, top_k=max_docs)

        if not results:
            self.logger.warning(f"No relevant documents found for: {topic}")
            return ""

        context_parts = []

        for i, doc in enumerate(results, 1):
            context_parts.append(f"[Document {i}: {doc['name']}]")
            # Take first 500 chars of each document
            snippet = doc['content'][:500]
            context_parts.append(snippet)
            context_parts.append("")

        context = "\n".join(context_parts)
        self.logger.info(f"Retrieved {len(results)} relevant documents")

        return context

    async def enhance_generation_with_rag(
        self,
        topic: str,
        audience: str,
        purpose: str,
        base_prompt: str
    ) -> str:
        """
        Enhance generation prompt with RAG context.

        Args:
            topic: Presentation topic
            audience: Target audience
            purpose: Presentation purpose
            base_prompt: Base generation prompt

        Returns:
            Enhanced prompt with context
        """
        # Retrieve relevant context
        context = self.retrieve_context(topic)

        if not context:
            return base_prompt

        # Enhance prompt with context
        enhanced_prompt = f"""You have access to the following relevant information from the knowledge base:

{context}

---

Use the above information to enhance your presentation outline where relevant.

{base_prompt}
"""

        return enhanced_prompt

    def add_knowledge(
        self,
        content: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add knowledge to the document store.

        Args:
            content: Knowledge content
            title: Knowledge title
            metadata: Optional metadata
        """
        filename = f"{title.replace(' ', '_')}.txt"
        self.document_store.add_document(content, filename, metadata)


class SimpleRAGGenerator:
    """Simple RAG-enhanced generation."""

    def __init__(
        self,
        knowledge_base_path: Optional[str] = None
    ):
        """
        Initialize simple RAG generator.

        Args:
            knowledge_base_path: Path to knowledge base directory
        """
        self.document_store = DocumentStore(knowledge_base_path)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_enhanced_requirements(
        self,
        topic: str,
        original_requirements: str = ""
    ) -> str:
        """
        Get enhanced requirements with knowledge base context.

        Args:
            topic: Presentation topic
            original_requirements: Original requirements

        Returns:
            Enhanced requirements string
        """
        context = self.document_store.search(topic, top_k=2)

        if not context:
            return original_requirements

        enhanced = f"{original_requirements}\n\nRelevant context from knowledge base:\n"

        for doc in context:
            enhanced += f"\n- {doc['name']}: {doc['content'][:200]}...\n"

        return enhanced
