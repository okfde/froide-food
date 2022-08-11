<template>
  <div class="container mb-5 mt-2">
    <div class="row" v-if="request">
      <div class="col-auto">
        <div v-if="loading" class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <h2>
          <a :href="request.url">{{ request.title }}</a>
        </h2>
        <p>
          Datum der Kontrollberichte in dieser Anfrage:
          <small v-for="d in reportDates" :key="d">{{ d }},</small>
        </p>
      </div>
      <div class="col-md-2">
        <button class="btn btn-secondary" @click.prevent="markUnresolved">
          Kein Ergebnis
        </button>
      </div>
      <div class="col-auto ms-auto">
        <button class="btn btn-light" @click.prevent="getNextRequest">
          Nächste Anfrage &rarr;
        </button>
      </div>
    </div>
    <food-report-request
      v-if="request"
      :request="request"
      @addreport="addReport"></food-report-request>
  </div>
</template>

<script>
import FoodReportRequest from './food-report-request'

import { getData, postData } from '~froide/frontend/javascript/lib/api.js'

export default {
  name: 'food-report',
  mixins: [],
  components: {
    FoodReportRequest
  },
  mounted() {
    this.getNextRequest()
  },
  data() {
    this.$root.csrfToken = document.querySelector(
      '[name=csrfmiddlewaretoken]'
    ).value

    return {
      request: null,
      loading: false,
      reportDates: []
    }
  },
  computed: {
    csrfToken() {
      return this.$root.csrfToken
    }
  },
  methods: {
    addReport(data) {
      if (data.reportdate) {
        this.reportDates.push(data.reportdate)
      }
      this.loading = true
      postData('', data, this.$root.csrfToken).then((result) => {
        this.loading = false
        if (data.unresolved) {
          this.getNextRequest()
        }
      })
    },
    markUnresolved() {
      this.addReport({
        foirequest: this.request.id,
        unresolved: true
      })
    },
    getNextRequest() {
      this.reportDates = []
      this.loading = true
      getData('').then((response) => {
        if (response.foirequest === null) {
          alert('Keine weiteren Anfragen mehr')
          return
        }
        getData(`/api/v1/request/${response.foirequest}/`).then((data) => {
          this.request = data
          this.loading = false
        })
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
