<script setup lang="ts">
import breadcrumb from './components/layouts/breadcrumb.vue';
import myheader from './components/layouts/header.vue';
import myfooter from './components/layouts/footer.vue';

</script>

<template>
  <div id="mainlayout">
    <el-container style="height: 100%;">
      <el-header>
        <myheader></myheader>
      </el-header>
      <el-main>
        <breadcrumb></breadcrumb>
        <router-view></router-view>
      </el-main>
      <el-footer>
        <myfooter></myfooter>
      </el-footer>
    </el-container>
  </div>
</template>

<style scoped>
#mainlayout {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #333131;
  box-shadow: 0 0 10px 5px rgba(0, 0, 0, 0.8);
}

.el-header,
.el-main,
.el-footer {
  padding: 0;
}

</style>
