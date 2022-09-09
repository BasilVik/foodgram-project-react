from api.pagination import PageLimitPagination
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import (FollowSerializer, SetPasswordSerializer,
                          UserDetailSerializer, UserSerializer)


class UserViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = User.objects.all()
    pagination_class = PageLimitPagination
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.check_password(request.data.get('current_password')):
            request.user.set_password(request.data.get('new_password'))
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = Follow.objects.filter(
            user=request.user
        ).select_related('author')
        serializer = FollowSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription, created = Follow.objects.get_or_create(
                user=request.user, author=author
            )
            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowSerializer(subscription)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        subscription = Follow.objects.filter(
            user=request.user, author=author
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя.!'},
            status=status.HTTP_400_BAD_REQUEST
        )
