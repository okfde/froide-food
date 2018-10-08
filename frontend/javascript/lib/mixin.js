import {renderDate, getPlaceStatus} from '../lib/utils'

const DAYS_BETWEEN_REQUEST = 90

var FoodItemMixin = {
  computed: {
    itemId () {
      return this.data.id
    },
    makeRequestUrl () {
      return `${this.config.requestUrl}?ident=${encodeURIComponent(this.data.ident)}`
    },
    hasRequest () {
      return this.lastRequest !== null
    },
    isSelected () {
      return this.data.id === this.selectedVenueId
    },
    starClass () {
      let suffix = ''
      let rating = this.data.rating
      if (rating !== Math.floor(rating)) {
        suffix = '-half'
        rating = Math.floor(rating)
      }
      return 'yelp-stars yelp-stars--small-' + rating + suffix
    },
    starRating () {
      return `Bewertung ${this.data.rating} Sterne`
    },
    lastRequest () {
      if (this.data.requests && this.data.requests.length > 0) {
        return this.data.requests[0]
      }
      return null
    },
    daysSinceLastRequest () {
      let requestDate = new Date(this.lastRequest.timestamp)
      let now = new Date()
      let difference = (now - requestDate) / (1000 * 60 * 60 * 24)
      return difference
    },
    lastRequestDate () {
      if (this.hasRequest) {
        return renderDate(this.lastRequest.timestamp)
      }
      return null
    },
    daysUntilNextRequest () {
      let days = DAYS_BETWEEN_REQUEST - this.daysSinceLastRequest
      return Math.max(0, Math.ceil(days))
    },
    canRequest () {
      if (this.lastRequest === null) {
        return true
      }
      return this.daysSinceLastRequest > DAYS_BETWEEN_REQUEST
    },
    requestComplete () {
      let status = getPlaceStatus(this.data)
      return status !== 'normal' && status !== 'pending'
    },
    requestStatusColor () {
      let status = getPlaceStatus(this.data)
      switch (status) {
        case 'normal':
          return [null, null]
        case 'success':
          return ['Anfrage erfolgreich', 'success']
        case 'failure':
          return ['Anfrage abgelehnt', 'danger']
        case 'pending':
          return ['Anfrage läuft', 'warning']
        case 'complete':
          return ['Anfrage abgeschlossen', 'info']
      }
    },
    requestStatus () {
      return this.requestStatusColor[0]
    },
    requestColor () {
      return 'text-' + this.requestStatusColor[1]
    },
    requestUrl () {
      if (this.hasRequest) {
        return this.lastRequest.url
      }
    }
  },
  methods: {
    setDetail () {
      this.$emit('detail', this.data)
    },
    startRequest () {
      this.$emit('startRequest', this.data)
    }
  }
}

export default FoodItemMixin
