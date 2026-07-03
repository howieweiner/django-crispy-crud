document.addEventListener('alpine:init', () => {
  Alpine.data('pagination', (pageSize) => ({
    pageSize: undefined,
    defaultPageSize: 10,
    localStorageKey: 'pageSize',
    init() {
      this.pageSize = pageSize
    },
    updatePageSize(pageSize) {
      const hiddenInput = document.getElementById('id_page_size')
      if (!hiddenInput) {
        console.warn('No hidden input element found for page size')
        return
      }
      hiddenInput.value = pageSize
      htmx.trigger(hiddenInput, 'change')
    },
  }))
})
