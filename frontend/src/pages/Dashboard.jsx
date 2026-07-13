const metrics = [
  { label: "업로드 문서", value: "0" },
  { label: "색인 완료", value: "0" },
  { label: "처리 중", value: "0" },
];

export default function Dashboard() {
  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-950">대시보드</h2>
        <p className="mt-1 text-sm text-gray-500">문서 처리 현황과 최근 활동을 확인합니다.</p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        {metrics.map((metric) => (
          <div key={metric.label} className="border border-gray-200 bg-white p-4">
            <p className="text-sm font-medium text-gray-500">{metric.label}</p>
            <p className="mt-2 text-2xl font-semibold text-gray-950">{metric.value}</p>
          </div>
        ))}
      </div>

      <div className="border border-dashed border-gray-300 bg-white p-6 text-sm text-gray-500">
        최근 업로드된 문서가 없습니다.
      </div>
    </section>
  );
}
