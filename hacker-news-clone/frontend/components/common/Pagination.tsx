interface PaginationProps {
  currentPage: number;
  totalPages: number;
  hasMore: boolean;
  onPageChange: (page: number) => void;
}

export default function Pagination({
  currentPage,
  totalPages,
  hasMore,
  onPageChange,
}: PaginationProps) {
  return (
    <div className="flex items-center justify-center space-x-4 py-6">
      {currentPage > 1 && (
        <button
          onClick={() => onPageChange(currentPage - 1)}
          className="text-sm text-gray-700 hover:underline"
        >
          &larr; Previous
        </button>
      )}

      <span className="text-sm text-gray-600">
        Page {currentPage} of {totalPages}
      </span>

      {hasMore && (
        <button
          onClick={() => onPageChange(currentPage + 1)}
          className="text-sm text-gray-700 hover:underline"
        >
          Next &rarr;
        </button>
      )}
    </div>
  );
}
