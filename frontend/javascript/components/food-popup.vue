<template>
  <div class="food-popup" :id="'popup-' + itemId">
    <h3>{{ data.name }}</h3>
    <div class="row">
      <div class="col-6">
        <p>
          <img :src="data.image" alt="Yelp venue image" class="venue-img img-fluid"/>
        </p>
      </div>
      <div class="col-6 food-popup-info">
        <p>{{ data.address }}</p>
        <a v-if="hasRequest" class="btn btn-success request-button" :href="data.request_url" target="_blank">
          zur Anfrage
        </a>
        <a v-else class="btn btn-primary request-button" :href="requestUrl"  target="_blank">Jetzt anfragen</a>
        <p>
          <small v-if="hasRequest">
            Anfrage wurde am {{ requestDate }} gestellt und {{ requestStatus }}.
          </small>
        </p>
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <a :href="data.url" class="provider-logo" target="_blank" rel="nooopener"></a>
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

.food-popup {
  h3 {
    max-width: 90vw;
    overflow: hidden;
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
  white-space: normal !important;
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
