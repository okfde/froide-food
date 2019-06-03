<template>
  <div class="container mt-5">
    <div>
      <h2>
        <a :href="request.url">{{ request.title }}</a>
        <button class="btn btn-secondary" @click.prevent="markUnresolved">
          Kein Ergebnis
        </button>
      </h2>
    </div>

    <food-report-message
      v-for="message in messages"
      :key="message.id"
      :message="message"
      :config="config"
      @addreport="addReport"
    ></food-report-message>
  </div>

</template>

<script>

import FoodReportMessage from './food-report-message'

// https://fragdenstaat.de/api/v1/request/47665/

export default {
  name: 'food-report-request',
  mixins: [],
  components: {
    FoodReportMessage
  },
  props: {
    config: {
      type: Object
    },
    request: {
      type: Object
    }
  },
  mounted () {
  },
  data () {
    return {}
  },
  computed: {
    csrfToken () {
      return this.$root.csrfToken
    },
    messages () {
      let messages = this.request.messages.filter((m, i) => {
        return m.is_response
      })
      messages.reverse()
      return messages
    }
  },
  methods: {
    addReport (data) {
      this.$emit('addreport', {
        ...data,
        foirequest: this.request.id
      })
    },
    markUnresolved () {
      this.$emit('addreport', {
        foirequest: this.request.id,
        unresolved: true
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
