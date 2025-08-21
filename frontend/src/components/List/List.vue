<script setup>
import { ref, onMounted } from 'vue';
import styles from './List.module.scss';

const filesList = ref(null)
const error = ref(null)

const fetchFiles = async () => {
  try {
    const response = await fetch('/api/getFiles')
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    
    const data = await response.json()
    filesList.value = data.files
  } catch (err) {
    console.error('Ошибка запроса:', err)
    error.value = 'Не удалось загрузить список файлов'
  }
}

onMounted(fetchFiles)
</script>

<template>
    <div v-if="filesList" :class=styles.container>
        <router-link 
            :to="`list/${item.name}`"
            :class=styles.link
            v-for="item in filesList"
        >
            <img
                :src="`../video-icon.svg`"
                :class=styles.item 
            >
            <div :class=styles.name>{{ item.name }}</div>
        </router-link>
    </div>
    <div v-else>Загрузка...</div>
</template>