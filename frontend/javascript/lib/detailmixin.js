var FoodDetailMixin = {
  methods: {
    getDetail (data) {
      this.fetching = true
      window.fetch(`/api/v1/venue/${data.ident}/?lat=${data.lat}&lng=${data.lng}&data=${encodeURIComponent(data.name)}&address=${encodeURIComponent(data.address)}&city=${encodeURIComponent(data.city)}`)
        .then((response) => {
          return response.json()
        }).then((data) => {
          if (data.error) {
            console.warn('Error requesting the API')
          }
          this.fetching = false
          this.$emit('detailfetched', data['result'])
        })
    }
  }
}

export default FoodDetailMixin
