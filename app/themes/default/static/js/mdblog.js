function modalEditPostForm(post_id, desc) {
    this.post_id = post_id;
    this.desc = desc;

    editpost.post_id.value = this.post_id;
    editpost.post.value = this.desc;
}