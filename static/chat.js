const form = document.querySelector("#chat-form");
const answer = document.querySelector("#answer");
const sourcesBox = document.querySelector("#sources");
const sourceList = document.querySelector("#source-list");
const documentSource = document.querySelector("#document-source");

function showSources(sources) {
  sourceList.replaceChildren();
  sources.forEach((source) => {
    const item = document.createElement("li");
    item.textContent = `${source.original_filename} (${source.page}쪽): ${source.text}`;
    sourceList.append(item);
  });
  const names = [...new Set(sources.map((source) => source.original_filename))];
  documentSource.textContent = `문서 출처: ${names.join(", ") || "없음"}`;
  sourcesBox.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  answer.textContent = "답변을 찾는 중입니다…";
  sourcesBox.hidden = true;
  const question = document.querySelector("#question").value;
  const stream = new EventSource(`/chat/stream?question=${encodeURIComponent(question)}`);
  stream.addEventListener("answer", (message) => {
    answer.textContent = JSON.parse(message.data).text;
  });
  stream.addEventListener("sources", (message) => showSources(JSON.parse(message.data)));
  stream.addEventListener("done", () => stream.close());
  stream.onerror = () => {
    answer.textContent = "답변 스트림을 연결하지 못했습니다.";
    stream.close();
  };
});
