ouroboros init start --llm-backend codex "
주제: 간단한 RAG 프로젝트를 만들기.

- 프로젝트 루트 폴더명: rag_test
- Docker Compose로 OpenSearch를 실행하고,
  프로젝트 폴더의 현대카드 상품설명서 PDF 2~3개를 이용해
  질문에 답하는 RAG 프로젝트를 만들고 싶습니다.
- PDF 파일 위치: rag_test/data/source/*
- 정교한 파싱이나 청킹, 에이전트 기능보다는
  PDF 적재, 임베딩, OpenSearch 저장, 검색, 답변 생성의
  전체 흐름이 정상적으로 동작하는 것이 중요합니다.

구현 요구사항:

- OpenSearch 적재 파이프라인은 rag_test/utils/ragger.py에
  Ragger 클래스 형태로 구현합니다.

- Ragger는 다음 구성요소를 인스턴스 변수로 가집니다.

  self.text_parser = TextParser()
  self.filter = Filter()
  self.text_splitter = TextSplitter()
  self.keyword_extractor = KeywordExtractor()
  self.embedder = Embedder()
  self.chunk_builder = ChunkBuilder()
  self.open_searcher = OpenSearcher()

- 각 구성요소의 역할:
  TextParser: PDF 텍스트 추출
  Filter: 불필요한 텍스트 정제
  TextSplitter: 텍스트 청킹
  KeywordExtractor: 키워드 추출
  Embedder: 임베딩 생성
  ChunkBuilder: OpenSearch에 저장할 하나의 청크 데이터 생성
  OpenSearcher: OpenSearch 인덱스 생성 및 데이터 적재

- Ragger의 run(...) 함수를 실행하면
  PDF 읽기부터 OpenSearch 적재까지 전체 RAG 전처리 파이프라인이 실행되어야 합니다.

- OpenSearcher라는 이름이 역할에 적절하지 않다면
  OpenSearchIndexer 또는 OpenSearchClient 등 더 적절한 이름으로 변경할 수 있습니다.

- 초보자가 이해할 수 있도록 각 클래스의 책임을 분리하고,
  타입 힌트와 README 실행 방법을 작성해주세요.
"