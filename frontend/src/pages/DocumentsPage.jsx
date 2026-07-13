import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import api from "../api/axios.js";

const MAX_UPLOAD_BYTES = 20 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".html", ".htm"];
const POLLING_INTERVAL_MS = 2500;

const statusMeta = {
  processing: {
    label: "처리 중",
    className: "bg-amber-100 text-amber-700",
  },
  indexed: {
    label: "완료",
    className: "bg-green-100 text-green-700",
  },
  failed: {
    label: "실패",
    className: "bg-red-100 text-red-700",
  },
};

function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  const code = detail?.error || error?.response?.data?.error;

  if (code === "file_too_large") {
    return "파일 크기가 20MB를 초과했습니다.";
  }
  if (code === "unsupported_format") {
    return "PDF, DOCX, HTML 파일만 업로드할 수 있습니다.";
  }
  if (code === "document_not_found") {
    return "이미 삭제되었거나 존재하지 않는 문서입니다.";
  }
  if (typeof code === "string") {
    return `요청 처리에 실패했습니다. (${code})`;
  }
  return "요청 처리 중 오류가 발생했습니다.";
}

function isAcceptedFile(file) {
  const lowerName = file.name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((extension) => lowerName.endsWith(extension));
}

function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function StatusBadge({ status }) {
  const meta = statusMeta[status] || {
    label: status,
    className: "bg-gray-100 text-gray-700",
  };

  return (
    <span className={`inline-flex min-w-[72px] items-center justify-center rounded-full px-2.5 py-1 text-xs font-semibold ${meta.className}`}>
      {status === "processing" && <span className="mr-1.5 h-2 w-2 animate-pulse rounded-full bg-amber-500" />}
      {meta.label}
    </span>
  );
}

function Toast({ toast, onClose }) {
  useEffect(() => {
    if (!toast) {
      return undefined;
    }

    const timerId = window.setTimeout(onClose, 3000);
    return () => window.clearTimeout(timerId);
  }, [onClose, toast]);

  if (!toast) {
    return null;
  }

  const colorClass = toast.type === "error" ? "bg-red-600" : toast.type === "success" ? "bg-green-600" : "bg-sky-600";

  return (
    <div className={`fixed bottom-4 right-4 z-50 rounded-lg px-4 py-3 text-sm font-medium text-white shadow-lg ${colorClass}`}>
      {toast.message}
    </div>
  );
}

export default function DocumentsPage() {
  const fileInputRef = useRef(null);
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [toast, setToast] = useState(null);

  const hasProcessingDocument = useMemo(
    () => documents.some((document) => document.status === "processing"),
    [documents],
  );

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type });
  }, []);

  const fetchDocuments = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) {
        setIsLoading(true);
      }

      try {
        const response = await api.get("/api/documents");
        setDocuments(response.data);
      } catch (error) {
        showToast(getErrorMessage(error), "error");
      } finally {
        if (!silent) {
          setIsLoading(false);
        }
      }
    },
    [showToast],
  );

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  useEffect(() => {
    if (!hasProcessingDocument) {
      return undefined;
    }

    const timerId = window.setInterval(() => {
      fetchDocuments({ silent: true });
    }, POLLING_INTERVAL_MS);

    return () => window.clearInterval(timerId);
  }, [fetchDocuments, hasProcessingDocument]);

  const uploadFile = async (file) => {
    if (!isAcceptedFile(file)) {
      showToast("PDF, DOCX, HTML 파일만 업로드할 수 있습니다.", "error");
      return;
    }

    if (file.size > MAX_UPLOAD_BYTES) {
      showToast("파일 크기가 20MB를 초과했습니다.", "error");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setIsUploading(true);

    try {
      await api.post("/api/documents", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      showToast("문서 업로드를 시작했습니다.", "success");
      await fetchDocuments({ silent: true });
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleFiles = (files) => {
    const [file] = Array.from(files);
    if (file) {
      uploadFile(file);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    if (!isUploading) {
      handleFiles(event.dataTransfer.files);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) {
      return;
    }

    setDeletingId(deleteTarget.documentId);
    try {
      await api.delete(`/api/documents/${deleteTarget.documentId}`);
      showToast("문서를 삭제했습니다.", "success");
      setDeleteTarget(null);
      await fetchDocuments({ silent: true });
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-950">문서 관리</h2>
        <p className="mt-1 text-sm text-gray-500">PDF, DOCX, HTML 문서를 업로드하고 색인 상태를 확인합니다.</p>
      </div>

      <div
        role="button"
        tabIndex={0}
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={[
          "rounded-xl border-2 border-dashed p-10 text-center transition-colors",
          isUploading ? "cursor-not-allowed opacity-70" : "cursor-pointer",
          isDragging ? "border-indigo-500 bg-indigo-50" : "border-gray-300 bg-gray-50 hover:border-indigo-400 hover:bg-indigo-50",
        ].join(" ")}
        aria-disabled={isUploading}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.html,.htm"
          className="sr-only"
          disabled={isUploading}
          onChange={(event) => handleFiles(event.target.files)}
        />
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-white text-2xl font-semibold text-indigo-600 shadow-sm">
          +
        </div>
        <p className="mt-4 text-sm font-semibold text-gray-800">
          {isUploading ? "업로드 요청 중입니다." : "파일을 끌어오거나 클릭해서 업로드"}
        </p>
        <p className="mt-2 text-sm text-gray-500">PDF, DOCX, HTML / 최대 20MB</p>
      </div>

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
          <h3 className="text-sm font-semibold text-gray-900">색인 문서 목록</h3>
          <button
            type="button"
            onClick={() => fetchDocuments()}
            className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-50"
          >
            새로고침
          </button>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-sm text-gray-500">문서 목록을 불러오는 중입니다.</div>
        ) : documents.length === 0 ? (
          <div className="p-10 text-center">
            <p className="text-sm font-semibold text-gray-800">아직 색인된 문서가 없습니다.</p>
            <p className="mt-2 text-sm text-gray-500">첫 문서를 업로드하면 처리 상태가 이 목록에 표시됩니다.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                <tr>
                  <th className="px-4 py-3">파일명</th>
                  <th className="px-4 py-3">상태</th>
                  <th className="px-4 py-3">업로드일</th>
                  <th className="px-4 py-3">페이지</th>
                  <th className="px-4 py-3">청크</th>
                  <th className="px-4 py-3 text-right">동작</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {documents.map((document) => (
                  <tr key={document.documentId} className="align-middle">
                    <td className="max-w-[280px] px-4 py-3">
                      <p className="truncate font-medium text-gray-900" title={document.filename}>
                        {document.filename}
                      </p>
                      {document.failReason && (
                        <p className="mt-1 truncate text-xs text-red-600" title={document.failReason}>
                          {document.failReason}
                        </p>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={document.status} />
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-gray-600">{formatDate(document.uploadedAt)}</td>
                    <td className="px-4 py-3 text-gray-600">{document.pageCount ?? 0}</td>
                    <td className="px-4 py-3 text-gray-600">{document.chunkCount ?? 0}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        type="button"
                        disabled={document.status === "processing"}
                        onClick={() => setDeleteTarget(document)}
                        className="rounded-lg px-3 py-1.5 text-sm font-semibold text-red-600 transition-colors hover:bg-red-50 disabled:cursor-not-allowed disabled:text-gray-400 disabled:hover:bg-transparent"
                        title={document.status === "processing" ? "처리 중인 문서는 삭제할 수 없습니다." : "문서 삭제"}
                      >
                        삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {deleteTarget && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 px-4">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-950">문서를 삭제할까요?</h3>
            <p className="mt-2 text-sm text-gray-500">
              "{deleteTarget.filename}" 문서와 색인 벡터가 함께 삭제됩니다.
            </p>
            <div className="mt-6 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setDeleteTarget(null)}
                className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
              >
                취소
              </button>
              <button
                type="button"
                onClick={confirmDelete}
                disabled={deletingId === deleteTarget.documentId}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {deletingId === deleteTarget.documentId ? "삭제 중" : "삭제"}
              </button>
            </div>
          </div>
        </div>
      )}

      <Toast toast={toast} onClose={() => setToast(null)} />
    </section>
  );
}
