<script setup>
    import { ref, watch, onMounted, onBeforeUnmount } from 'vue';

    const props = defineProps({
        videoUrl: String
    })

    const plyr = ref(null);

    watch(() => props.videoUrl, (newUrl) => {
        if (plyr.value && newUrl) {
            plyr.value.player.source = {
            type: 'video',
                sources: [{
                    src: newUrl,
                    type: 'video/mp4'
                }]
            };
        }
    });
</script>

<template>
    <vue-plyr ref="plyr">
        <video
            controls
            playsinline
        >
            <source size='720' type="video/mp4" :src="videoUrl" />
        </video>
    </vue-plyr>
</template>
