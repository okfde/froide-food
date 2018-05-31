<template>
  <div class="food-popup" :id="'popup-' + itemId">
    <div class="row">
      <div class="col-12">
        <h4>{{ data.name }}</h4>
        <p class="venue-address">{{ data.address }}</p>
        <a :href="data.url" class="provider-logo" target="_blank" rel="noopener"></a>
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <a v-if="!data.request_status" class="request-button" :href="requestUrl"  target="_blank">
          Hygienekontrolle anfragen&nbsp;&rarr;
        </a>
        <a v-else class="to-request-button" :href="data.request_url" target="_blank">
          zur Anfrage&nbsp;&rarr;
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import FoodItemMixin from '../lib/mixin'

export default {
  name: 'food-popup',
  mixins: [FoodItemMixin],
  props: {
    data: {
      type: Object
    }
  }
}
</script>

<style lang="scss" scoped>

.image-column {
  padding: 0 5px;
}

.info-column {
  padding: 0 5px;
}

.venue-img {
  height: 70px;
  width: 100%;
  object-fit: cover;
}

.venue-address {
  color: #687683;
  font-size: 1rem;
  display: inline-block;
  margin: 0 0 0.5rem;
  white-space: pre-line;
}

.request-button {
  display: block;
  font-size: 1rem;
}

.to-request-button {
  display: block;
  font-size: 1rem;
  color: #28a745;
}

.provider-logo {
  background-image: url('/static/food/images/yelp_logo.png');
  background-repeat: no-repeat;
  background-size: contain;
  display: inline-block;
  float: right;
  width: 65px;
  height: 40px;
  margin: 0.5rem 0 0 0.25rem;
}


</style>
