<template>
  <div class="container mt-2">
    <FoodReportMessage
      v-for="message in messages"
      :key="message.id"
      :message="message"
      :request="request"
      @addreport="addReport"
    ></FoodReportMessage>
  </div>
</template>

<script>
import FoodReportMessage from './food-report-message'

// https://fragdenstaat.de/api/v1/request/47665/

export default {
  name: 'FoodReportRequest',
  mixins: [],
  components: {
    FoodReportMessage
  },
  props: {
    request: {
      type: Object,
      required: true
    }
  },
  emits: ['addreport'],
  mounted() {},
  data() {
    return {}
  },
  computed: {
    messages() {
      const messages = this.request.messages.filter((m) => {
        return m.is_response
      })
      messages.reverse()
      return messages
    }
  },
  methods: {
    addReport(data) {
      this.$emit('addreport', {
        ...data,
        foirequest: this.request.id
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.loading {
  height: 100vh;
  padding-top: 30%;
  background-color: #fff;
  // animation: blinker 0.8s linear infinite;
  text-align: center;
}

.loading img {
  width: 10%;
}

@keyframes blinker {
  50% {
    opacity: 0.25;
  }
}
</style>
