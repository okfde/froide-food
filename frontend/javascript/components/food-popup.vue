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
          <p>
            <a v-if="requestUrl" :href="requestUrl" target="_blank">
              zur Anfrage&nbsp;&rarr;
            </a>
            <span v-else>Anfrage gestellt!</span>
          </p>
          <p v-if="requestComplete">
            <a :href="requestUrl" target="_blank" @click.prevent="setDetail">
              zu den Berichten&nbsp;&rarr;
            </a>
          </p>
        </div>
        <p v-if="canRequest">
          <a
            @click.prevent.stop="startRequest"
            class="btn btn-primary btn-sm"
            :href="makeRequestUrl"
            target="_blank">
            Hygienekontrolle anfragen&nbsp;&rarr;
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import FoodItemMixin from '../lib/mixin'

export default {
  name: 'FoodPopup',
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
.btn.btn-primary {
  color: var(--bs-btn-color) !important;
}
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
  font-size: 1rem;
  display: inline-block;
  margin: 0 0 0.5rem;
  white-space: pre-line;
}

.to-request-button {
  display: block;
  font-size: 1rem;
  color: var(--bs-success);
}

.request-status {
  font-size: 0.9rem;
}
</style>
