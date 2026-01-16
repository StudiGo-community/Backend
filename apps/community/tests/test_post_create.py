# User 부분 완성 후 테스트 가능


# from typing import Any, cast
#
# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
#
# from apps.community.models.post_images import PostImage
# from apps.community.models.posts import Post
#
# User = get_user_model()
#
#
# class PostCreateAPITest(APITestCase):
#     def setUp(self) -> None:
#         self.user = User.objects.create(
#             name="tester",
#             password="pass1234!",
#         )
#         self.url = reverse("post-create")
#
#     def test_create_post_unauthorized(self) -> None:
#         payload = {
#             "title": "게시글 제목",
#             "content": "내용",
#             "category": "Free",
#         }
#         response = self.client.post(self.url, payload, format="json")
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_create_post_success_with_images(self) -> None:
#         self.client.force_authenticate(user=self.user)
#
#         payload = {
#             "title": "게시글 제목",
#             "content": "내용",
#             "category": "Free",
#             "images": [
#                 {"url": "https://cdn.example.com/2.png", "order": 2},
#                 {"url": "https://cdn.example.com/1.png", "order": 1},
#             ],
#         }
#
#         response = self.client.post(self.url, payload, format="json")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
#         data = response.json()
#         self.assertIn("id", data)
#         self.assertEqual(data["title"], "게시글 제목")
#         self.assertEqual(data["content"], "내용")
#         self.assertEqual(data["category"], "Free")
#         self.assertEqual(data["status"], "ACTIVE")
#         self.assertEqual(data["like_count"], 0)
#         self.assertEqual(data["comment_count"], 0)
#
#         # images 응답 구조 확인
#         self.assertEqual(len(data["images"]), 2)
#         self.assertEqual(
#             data["images"][0]["image_url"], "https://cdn.example.com/1.png"
#         )
#         self.assertEqual(data["images"][0]["sort_order"], 1)
#
#         # DB 저장 확인
#         post_id = data["id"]
#         post = cast(Any, Post).objects.get(pk=post_id)
#         self.assertEqual(post.author_id, self.user.id)
#
#         self.assertEqual(cast(Any, PostImage).objects.filter(post=post).count(), 2)
#
#     def test_create_post_invalid_images_duplicate_order(self) -> None:
#         self.client.force_authenticate(user=self.user)
#
#         payload = {
#             "title": "제목",
#             "content": "내용",
#             "category": "Free",
#             "images": [
#                 {"url": "https://cdn.example.com/1.png", "order": 1},
#                 {"url": "https://cdn.example.com/2.png", "order": 1},
#             ],
#         }
#         response = self.client.post(self.url, payload, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
