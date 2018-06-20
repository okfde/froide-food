import {renderDate} from '../lib/utils'

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
      return this.data.id === this.selectedFacilityId
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
      return this.data.requests.some((r) => r.status === 'resolved')
    },
    requestStatusColor () {
      if (this.hasRequest) {
        if (this.lastRequest.status === 'resolved') {
          if (this.lastRequest.resolution === 'successful' ||
              this.lastRequest.resolution === 'partially_successful') {
            return ['Anfrage erfolgreich', 'success']
          } else if (this.lastRequest.resolution === 'refused') {
            return ['Anfrage abgelehnt', 'danger']
          } else {
            return ['Anfrage abgeschlossen', 'info']
          }
        } else if (this.lastRequest.status === 'awaiting_response' ||
                   this.lastRequest.status === 'awaiting_user_confirmation') {
          return ['Anfrage läuft', 'warning']
        }
      }
      return [null, null]
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
    }
  }
}

export default FoodItemMixin
