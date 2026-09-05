import { useState, useCallback } from 'react'
import { useToast } from '@/components/ui/toast'

interface UseDeleteFlowOptions<T> {
  /** API delete function */
  deleteFn: (id: number) => Promise<any>
  /** Label for toast messages (e.g. 'Resume', 'Job', 'Match') */
  itemLabel: string
  /** Called after successful deletion to update local state */
  onDeleted: (id: number) => void
  /** Optionally derive a description from the pending item */
  getDescription?: (item: T) => string
}

interface UseDeleteFlowResult<T> {
  /** The item currently pending deletion confirmation */
  pendingDelete: T | null
  /** Whether a delete request is in flight */
  deleting: boolean
  /** Initiate the confirmation dialog for an item */
  requestDelete: (item: T, e?: React.MouseEvent) => void
  /** Dismiss the confirmation dialog */
  cancelDelete: () => void
  /** Execute the confirmed deletion */
  handleDelete: () => Promise<void>
}

export function useDeleteFlow<T extends { id: number }>({
  deleteFn,
  itemLabel,
  onDeleted,
  getDescription,
}: UseDeleteFlowOptions<T>): UseDeleteFlowResult<T> {
  const [pendingDelete, setPendingDelete] = useState<T | null>(null)
  const [deleting, setDeleting] = useState(false)
  const { addToast } = useToast()

  const requestDelete = useCallback((item: T, e?: React.MouseEvent) => {
    e?.stopPropagation()
    setPendingDelete(item)
  }, [])

  const cancelDelete = useCallback(() => {
    setPendingDelete(null)
  }, [])

  const handleDelete = useCallback(async () => {
    if (!pendingDelete) return

    try {
      setDeleting(true)
      const deletedId = pendingDelete.id
      const description = getDescription?.(pendingDelete) ?? `${itemLabel} #${deletedId}`

      await deleteFn(deletedId)
      onDeleted(deletedId)
      addToast({
        type: 'success',
        title: `${itemLabel} deleted`,
        description: `${description} has been removed.`,
      })
      setPendingDelete(null)
    } catch (err: any) {
      console.error('Delete error:', err)
      addToast({
        type: 'error',
        title: 'Delete failed',
        description: err.response?.data?.detail || `Failed to delete ${itemLabel.toLowerCase()}`,
      })
    } finally {
      setDeleting(false)
    }
  }, [pendingDelete, deleteFn, itemLabel, onDeleted, getDescription, addToast])

  return { pendingDelete, deleting, requestDelete, cancelDelete, handleDelete }
}
