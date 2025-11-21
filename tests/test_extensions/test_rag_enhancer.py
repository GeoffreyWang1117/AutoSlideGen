"""
Tests for RAG enhancer extension.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from autoslidegen.extensions.rag_enhancer import (
    DocumentStore,
    RAGEnhancer,
    SimpleRAGGenerator
)


class TestDocumentStore:
    """Tests for DocumentStore."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def doc_store(self, temp_dir):
        """Create DocumentStore instance."""
        return DocumentStore(kb_path=temp_dir)

    @pytest.fixture
    def sample_docs(self, temp_dir):
        """Create sample documents."""
        doc1 = Path(temp_dir) / 'doc1.txt'
        doc1.write_text('人工智能是计算机科学的一个分支。机器学习是AI的核心技术。')

        doc2 = Path(temp_dir) / 'doc2.md'
        doc2.write_text('深度学习基于神经网络。卷积神经网络用于图像识别。')

        return [str(doc1), str(doc2)]

    def test_initialization(self, doc_store):
        """Test DocumentStore initialization."""
        assert Path(doc_store.kb_path).exists()
        assert isinstance(doc_store.documents, list)

    def test_add_document(self, doc_store):
        """Test adding a document."""
        doc_store.add_document(
            content="这是测试文档内容",
            name="test_doc",
            metadata={'author': 'Test'}
        )

        assert len(doc_store.documents) == 1
        assert doc_store.documents[0]['name'] == 'test_doc'
        assert doc_store.documents[0]['metadata']['author'] == 'Test'

    def test_load_documents_from_directory(self, doc_store, sample_docs):
        """Test loading documents from directory."""
        doc_store.load_from_directory()

        assert len(doc_store.documents) >= 2

    def test_search_documents(self, doc_store):
        """Test searching documents."""
        doc_store.add_document("人工智能是未来的趋势", "doc1")
        doc_store.add_document("机器学习算法很重要", "doc2")
        doc_store.add_document("深度学习模型很复杂", "doc3")

        results = doc_store.search("人工智能", top_k=2)

        assert len(results) <= 2
        assert isinstance(results, list)
        if len(results) > 0:
            assert 'score' in results[0]
            assert 'content' in results[0]

    def test_search_no_results(self, doc_store):
        """Test search with no matching documents."""
        doc_store.add_document("完全不相关的内容", "doc1")

        results = doc_store.search("人工智能")

        assert len(results) == 0

    def test_search_case_insensitive(self, doc_store):
        """Test that search is case-insensitive."""
        doc_store.add_document("Artificial Intelligence is important", "doc1")

        results = doc_store.search("ARTIFICIAL")

        assert len(results) > 0

    def test_get_all_documents(self, doc_store):
        """Test getting all documents."""
        doc_store.add_document("Doc 1", "doc1")
        doc_store.add_document("Doc 2", "doc2")

        all_docs = doc_store.get_all_documents()

        assert len(all_docs) == 2

    def test_clear_documents(self, doc_store):
        """Test clearing all documents."""
        doc_store.add_document("Test", "doc1")
        doc_store.clear()

        assert len(doc_store.documents) == 0

    def test_load_txt_file(self, doc_store, temp_dir):
        """Test loading .txt file."""
        txt_file = Path(temp_dir) / 'test.txt'
        txt_file.write_text('测试内容')

        doc_store.load_from_directory()

        assert len(doc_store.documents) > 0

    def test_load_md_file(self, doc_store, temp_dir):
        """Test loading .md file."""
        md_file = Path(temp_dir) / 'test.md'
        md_file.write_text('# 标题\n测试内容')

        doc_store.load_from_directory()

        assert len(doc_store.documents) > 0


class TestRAGEnhancer:
    """Tests for RAGEnhancer."""

    @pytest.fixture
    def doc_store(self):
        """Create DocumentStore with sample data."""
        store = DocumentStore()
        store.add_document(
            "人工智能包括机器学习、深度学习、自然语言处理等技术",
            "ai_basics"
        )
        store.add_document(
            "机器学习分为监督学习、无监督学习和强化学习",
            "ml_types"
        )
        return store

    @pytest.fixture
    def rag_enhancer(self, doc_store):
        """Create RAGEnhancer instance."""
        return RAGEnhancer(doc_store)

    def test_initialization(self, rag_enhancer):
        """Test RAGEnhancer initialization."""
        assert rag_enhancer.doc_store is not None

    def test_retrieve_relevant_context(self, rag_enhancer):
        """Test retrieving relevant context."""
        context = rag_enhancer.retrieve_relevant_context(
            query="机器学习",
            top_k=2
        )

        assert isinstance(context, str)
        assert len(context) > 0

    def test_retrieve_empty_context(self):
        """Test retrieving context with empty doc store."""
        empty_store = DocumentStore()
        enhancer = RAGEnhancer(empty_store)

        context = enhancer.retrieve_relevant_context("test")

        assert context == ""

    def test_enhance_prompt(self, rag_enhancer):
        """Test enhancing prompt with RAG context."""
        original_prompt = "请介绍人工智能的应用"

        enhanced = rag_enhancer.enhance_prompt(
            original_prompt,
            topic="人工智能"
        )

        assert isinstance(enhanced, str)
        assert len(enhanced) >= len(original_prompt)

    def test_enhance_requirements(self, rag_enhancer):
        """Test enhancing requirements."""
        original = "重点介绍实际应用"

        enhanced = rag_enhancer.enhance_requirements(
            topic="机器学习",
            original_requirements=original
        )

        assert isinstance(enhanced, str)


class TestSimpleRAGGenerator:
    """Tests for SimpleRAGGenerator."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with sample docs."""
        temp_dir = tempfile.mkdtemp()

        # Create sample knowledge base files
        (Path(temp_dir) / 'ai.txt').write_text('人工智能相关内容')
        (Path(temp_dir) / 'ml.md').write_text('机器学习相关内容')

        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def rag_gen(self, temp_dir):
        """Create SimpleRAGGenerator instance."""
        return SimpleRAGGenerator(knowledge_base_path=temp_dir)

    def test_initialization(self, rag_gen):
        """Test SimpleRAGGenerator initialization."""
        assert rag_gen.enhancer is not None
        assert rag_gen.doc_store is not None

    def test_get_enhanced_requirements(self, rag_gen):
        """Test getting enhanced requirements."""
        enhanced = rag_gen.get_enhanced_requirements(
            topic="人工智能",
            original_requirements="重点关注应用"
        )

        assert isinstance(enhanced, str)
        assert len(enhanced) > 0

    def test_get_enhanced_requirements_no_original(self, rag_gen):
        """Test enhanced requirements without original requirements."""
        enhanced = rag_gen.get_enhanced_requirements(
            topic="机器学习",
            original_requirements=None
        )

        assert isinstance(enhanced, str)

    def test_search_knowledge_base(self, rag_gen):
        """Test searching knowledge base."""
        results = rag_gen.search_knowledge_base("人工智能", top_k=3)

        assert isinstance(results, list)
        # May or may not have results depending on content matching

    def test_empty_knowledge_base(self):
        """Test with empty knowledge base."""
        import tempfile
        temp_dir = tempfile.mkdtemp()

        try:
            rag_gen = SimpleRAGGenerator(knowledge_base_path=temp_dir)
            enhanced = rag_gen.get_enhanced_requirements("test", "requirements")

            # Should handle gracefully
            assert isinstance(enhanced, str)
        finally:
            shutil.rmtree(temp_dir)

    def test_reload_knowledge_base(self, rag_gen, temp_dir):
        """Test reloading knowledge base."""
        # Add new document
        (Path(temp_dir) / 'new.txt').write_text('新增内容')

        # Reload
        rag_gen.reload_knowledge_base()

        # Should have more documents now
        all_docs = rag_gen.doc_store.get_all_documents()
        assert len(all_docs) >= 2
