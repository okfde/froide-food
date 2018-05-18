<template>
  <div class="loader"></div>
</template>

<script>

export default {
  name: 'food-loader'
}
</script>

<style>
.loader,
.loader:after {
  border-radius: 50%;
  width: 1rem;
  height: 1rem;
  display: inline-block;
}
.loader {
  margin-bottom: -0.15rem;
  position: relative;
  border-top: 0.1rem solid rgba(255,255,255, 0.2);
  border-right: 0.1rem solid rgba(255,255,255, 0.2);
  border-bottom: 0.1rem solid rgba(255,255,255, 0.2);
  border-left: 0.1rem solid #ffffff;
  -webkit-transform: translateZ(0);
  -ms-transform: translateZ(0);
  transform: translateZ(0);
  -webkit-animation: load8 1.1s infinite linear;
  animation: load8 1.1s infinite linear;
}
@-webkit-keyframes load8 {
  0% {
    -webkit-transform: rotate(0deg);
    transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}
@keyframes load8 {
  0% {
    -webkit-transform: rotate(0deg);
    transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}
</style>
