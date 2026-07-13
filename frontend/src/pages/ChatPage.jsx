export default function ChatPage() {
  return (
    <section className="grid min-h-[520px] grid-rows-[1fr_auto] border border-gray-200 bg-white">
      <div className="space-y-4 p-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-950">Q&A 채팅</h2>
          <p className="mt-1 text-sm text-gray-500">색인된 문서를 근거로 질문에 답변합니다.</p>
        </div>
        <div className="border border-dashed border-gray-300 p-6 text-sm text-gray-500">
          아직 대화가 없습니다.
        </div>
      </div>

      <form className="border-t border-gray-200 p-4">
        <label className="sr-only" htmlFor="question">
          질문
        </label>
        <div className="flex gap-2">
          <textarea
            id="question"
            className="min-h-12 flex-1 resize-none border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="질문을 입력하세요"
            rows="1"
          />
          <button
            className="h-12 bg-gray-950 px-4 text-sm font-semibold text-white transition hover:bg-gray-800"
            type="submit"
          >
            전송
          </button>
        </div>
      </form>
    </section>
  );
}
