export default function DocumentsPage() {
  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-950">문서 관리</h2>
        <p className="mt-1 text-sm text-gray-500">PDF, DOCX, HTML 문서를 업로드하고 색인 상태를 확인합니다.</p>
      </div>

      <div className="border border-dashed border-gray-300 bg-white p-8 text-center">
        <p className="text-sm font-medium text-gray-700">업로드 영역</p>
        <p className="mt-2 text-sm text-gray-500">Phase 6에서 드래그앤드롭 업로드와 문서 목록을 연결합니다.</p>
      </div>
    </section>
  );
}
