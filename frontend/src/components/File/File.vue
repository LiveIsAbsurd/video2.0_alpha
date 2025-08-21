<script setup>
    const props = defineProps({
        id: String
    })

    const privateKey = ref('');
    const encryptedBlob = ref(null);

    import { openDB } from 'idb';
    import { onMounted, ref } from 'vue';
    import Player from '../Player/Player.vue';
    import * as openpgp from "openpgp";
    import styles from "./File.module.scss";

    const downloadProgress = ref(0);
    const isDownloading = ref(false);
    const isDecrypting = ref(false);
    const downloadError = ref(null);
    const videoURL = ref(null);
    const showDecryptForm = ref(false);
    const dbName = 'videoStorage';
    const dbVersion = 2;

    const initDB = async () => {
        return await openDB(dbName, dbVersion, {
            upgrade(db, oldVersion) {
                if (oldVersion < 1) {
                    db.createObjectStore('files', { keyPath: 'id' });
                    db.createObjectStore('encryptedFiles', { keyPath: 'id' });
                }
                if (oldVersion < 2 && !db.objectStoreNames.contains('encryptedFiles')) {
                    db.createObjectStore('encryptedFiles', { keyPath: 'id' });
                }
            },
        });
    }

    const saveEncryptedFile = async (id, fileData) => {
        try {
            const db = await initDB();
            const tx = db.transaction('encryptedFiles', 'readwrite');
            await tx.store.put({ id, data: fileData });
            await tx.done;
            return true;
        } catch (error) {
            console.error('Ошибка сохранения зашифрованного файла:', error);
            downloadError.value = 'Ошибка сохранения файла';
            return false;
        }
    }

    const downloadFile = async (fileUrl, fileName) => {
        try {
            downloadProgress.value = 0;
            isDownloading.value = true;
            downloadError.value = null;

            const response = await fetch(fileUrl);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const contentLength = response.headers.get('content-length');
            const totalBytes = parseInt(contentLength || '0', 10);
            let loadedBytes = 0;

            const reader = response.body.getReader();
            const chunks = [];

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;

                chunks.push(value);
                loadedBytes += value.length;

                if (totalBytes > 0) {
                    downloadProgress.value = Math.round((loadedBytes / totalBytes) * 100);
                }
            }

            const blob = new Blob(chunks);
            const saveResult = await saveEncryptedFile(fileName, blob);

            if (saveResult) {
                downloadProgress.value = 100;
                return blob;
            }

        } catch (error) {
            console.error('Ошибка загрузки файла:', error);
            downloadError.value = 'Ошибка загрузки файла';
        } finally {
            isDownloading.value = false;
        }

        return null;
    }

    const decryptFile = async () => {
        if (!privateKey.value) {
            downloadError.value = 'Пожалуйста, введите ключ расшифровки';
            return;
        }

        try {
            isDecrypting.value = true;
            downloadError.value = null;
            
            const encryptedData = await new Response(encryptedBlob.value).arrayBuffer();
            
            const privateKeyObj = await openpgp.readPrivateKey({ 
                armoredKey: privateKey.value 
            });
            
            const message = await openpgp.readMessage({
                binaryMessage: new Uint8Array(encryptedData)
            });
            
            const { data: decryptedData } = await openpgp.decrypt({
                message,
                decryptionKeys: privateKeyObj,
                format: 'binary',
            });
            
            const decryptedBlob = new Blob([decryptedData], { type: 'video/mp4' });
            videoURL.value = URL.createObjectURL(decryptedBlob);
            
            const db = await initDB();
            const tx = db.transaction('files', 'readwrite');
            await tx.store.put({ id: props.id, data: decryptedBlob });
            await tx.done;
            
        } catch (error) {
            console.error('Ошибка расшифровки:', error);
            downloadError.value = 'Ошибка расшифровки файла. Проверьте ключ.';
            return null;
        } finally {
            isDecrypting.value = false;
        }
    }

    const DownloadOnMount = async () => {
        try {
            const db = await initDB();
            
            const decryptedFileData = await db.get('files', props.id);
            if (decryptedFileData) {
                videoURL.value = URL.createObjectURL(decryptedFileData.data);
                return;
            }
            
            const encryptedFileData = await db.get('encryptedFiles', props.id);
            if (encryptedFileData) {
                encryptedBlob.value = encryptedFileData.data;
                showDecryptForm.value = true;
                return;
            }
            
            const downloadedBlob = await downloadFile(
                `/files/${props.id}`,
                props.id
            );
            
            if (downloadedBlob) {
                encryptedBlob.value = downloadedBlob;
                showDecryptForm.value = true;
            }
            
        } catch (error) {
            console.error('Ошибка в DownloadOnMount:', error);
            downloadError.value = 'Ошибка при обработке файла';
        }
    }

    async function clearAllFiles() {
        try {
            const db = await initDB();
            const tx1 = db.transaction('files', 'readwrite');
            await tx1.store.clear();
            await tx1.done;
            
            const tx2 = db.transaction('encryptedFiles', 'readwrite');
            await tx2.store.clear();
            await tx2.done;
            
            console.log('Все файлы удалены');
            return true;
        } catch (error) {
            console.error('Ошибка очистки:', error);
            return false;
        }
    }
    
    onMounted(() => DownloadOnMount());
</script>

<template>
    <div v-if="!videoURL" :class=styles.info>
        <div v-if="isDownloading" :class=styles.text>
            Загрузка файла...
            <a-progress type="circle" :percent=downloadProgress />
        </div>
        
        <div v-if="showDecryptForm && !isDownloading" :class=styles.text>
            <div v-if="!isDecrypting" :class=styles.text>Введите ключ для расшифровки</div>
            <textarea v-if="!isDecrypting" v-model="privateKey" :class=styles.keyInput placeholder="Вставьте PGP приватный ключ здесь"></textarea>
            <button 
                v-if="!isDecrypting"
                @click="decryptFile" 
                :disabled="!privateKey"
                :class=styles.decryptButton
            >
                <div>Расшифровать</div>
            </button>
            <div v-if="isDecrypting" :class=styles.spin>
                <div>Расшифровка...</div>
                <a-spin size="large" />
            </div>
        </div>
    </div>
    <!-- <button @click="clearAllFiles">удалить</button> -->
    <div v-if="downloadError" class="error">{{ downloadError }}</div>
    <Player v-if="videoURL" :video-url="videoURL" />
</template>

<style scoped>
    .error {
        color: red;
    }
</style>