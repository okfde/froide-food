<template>
  <div class="food-popup">
    <h3>{{ data.name }}</h3>
    <div class="row ">
      <div class="col-6">
        <p>
          <img :src="data.image" alt="Yelp venue image" class="venue-img img-fluid"/>
        </p>
      </div>
      <div class="col-6 food-popup-info">
        <p>{{ data.address }}</p>
        <p>
          <a class="btn btn-primary request-button" :href="requestUrl">Anfragen</a>
        </p>
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <a :href="data.url" class="provider-logo"></a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'food-popup',
  props: {
    data: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    requestUrl () {
      return `./anfragen/?ident=${encodeURIComponent(this.data.ident)}`
    }
  }
}
</script>

<style lang="scss" scoped>

.food-popup {
  h3 {
    min-width: 200px;
  }
  p {
    margin: 0 0 1rem !important;
  }
}

.venue-img {
  height: 120px;
  width: 100%;
  object-fit: cover;
}

.request-button {
  color: #fff !important;
}


.provider-logo {
  background-image: url('/static/food/images/yelp_logo.png');
  background-repeat: no-repeat;
  background-size: contain;
  display: inline-block;
  width: 80px;
  height: 40px;
  // margin: 1rem 2rem;
  float: right;
}

</style>
