var FoodItemMixin = {
  computed: {
    itemId () {
      return this.data.id
    },
    requestUrl () {
      return `${this.config.requestUrl}?ident=${encodeURIComponent(this.data.ident)}`
    },
    hasRequest () {
      return this.data.request_url !== null
    },
    requestDate () {
      if (this.hasRequest) {
        let d = (new Date(this.data.request_timestamp))
        return `${d.getDate()}.${d.getMonth()}.${d.getFullYear()}`
      }
      return null
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
    requestStatus () {
      if (this.hasRequest) {
        if (this.data.request_status === 'resolved') {
          return 'ist abgeschlossen'
        } else if (this.data.request_status === 'awaiting_response') {
          return 'läuft noch'
        } else if (this.data.request_status === 'awaiting_user_confirmation') {
          return 'läuft noch'
        }
      }
      return null
    }
  }
}

export default FoodItemMixin
