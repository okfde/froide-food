var FoodItemMixin = {
  computed: {
    itemId () {
      return this.data.id
    },
    requestUrl () {
      return `./anfragen/?ident=${encodeURIComponent(this.data.ident)}`
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
