<template>
  <img :src="spinner" alt="wird geladen" width="25"/>
</template>

<script>

export default {
  name: 'food-loader',
  props: {
    staticUrl: String,
  },
  computed: {
    spinner () {
      return this.$root.config.staticUrl + 'img/spinner.svg'
    }
  }
}
</script>
