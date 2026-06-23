import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const loading = ref(false)
  const showModal = ref(false)
  const modalComponent = ref(null)
  const modalProps = ref({})

  function openModal(component, props = {}) {
    modalComponent.value = component
    modalProps.value = props
    showModal.value = true
  }

  function closeModal() {
    showModal.value = false
    modalComponent.value = null
    modalProps.value = {}
  }

  return { loading, showModal, modalComponent, modalProps, openModal, closeModal }
})
