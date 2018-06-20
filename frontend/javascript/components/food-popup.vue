<template>
  <div class="food-popup" :id="'popup-' + itemId">
    <div class="row">
      <div class="col-12">
        <h4 class="venue-name">{{ data.name }}</h4>
        <p class="venue-address">{{ data.address }}</p>
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <div v-if="hasRequest" class="request-status">
          <p :class="requestColor">
            {{ requestStatus }}
          </p>
          <p v-if="requestComplete">
            <a :href="requestUrl" target="_blank" @click.prevent="setDetail">
              zu den Berichten&nbsp;&rarr;
            </a>
          </p>
          <p v-else>
            <a :href="requestUrl" target="_blank">
              zur Anfrage&nbsp;&rarr;
            </a>
          </p>
        </div>
        <p v-if="canRequest">
          <a class="btn btn-primary btn-sm make-request-btn" :href="makeRequestUrl"  target="_blank">
            Hygienekontrolle<br class="d-block d-sm-none"/>
            anfragen&nbsp;&rarr;
          </a>
        </p>
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
    },
    config: {
      type: Object
    }
  }
}
</script>

<style lang="scss" scoped>

.venue-name {
  min-width: 240px;
}

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

.to-request-button {
  display: block;
  font-size: 1rem;
  color: #28a745;
}

.make-request-btn {
  color: white;
  white-space: normal !important;
}

.request-status {
  font-size: 0.9rem;
}

</style>
