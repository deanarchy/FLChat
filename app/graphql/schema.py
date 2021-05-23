import graphene as gp
from graphql import GraphQLError
from graphene_sqlalchemy import SQLAlchemyObjectType
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    current_user,
)
from ..models import (
    User as UserModel,
    Message as MessageModel,
    Conversation as ConversationModel,
)

from .. import db
from .decorators import admin_required


class Conversation(SQLAlchemyObjectType):
    class Meta:
        model = ConversationModel


class Message(SQLAlchemyObjectType):
    class Meta:
        model = MessageModel


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        exclude_fields = ('password_hash',)


class CreateUser(gp.Mutation):
    class Arguments:
        email = gp.String()
        phone = gp.String()
        first_name = gp.String()
        last_name = gp.String()
        password = gp.String()
        password_confirm = gp.String()

    success = gp.Boolean()
    user = gp.Field(lambda: User)

    def mutate(
            root_value, info,
            email, password, password_confirm,
            first_name, last_name=None,
            phone=None
    ):
        if UserModel.query.filter_by(email=email).first():
            raise GraphQLError('user already exists!')
        if password != password_confirm:
            raise GraphQLError('password does not match')

        user = UserModel(
            email=email, phone=phone, first_name=first_name,
            last_name=last_name, password=password
        )

        db.session.add(user)
        db.session.commit()

        success = True

        return CreateUser(user=user, success=success)


class DeleteUser(gp.Mutation):
    class Arguments:
        email = gp.String()

    success = gp.Boolean()
    user = gp.Field(lambda: User)

    @jwt_required()
    def mutate(root_value, info, email=None):

        user = current_user

        if email:
            if not current_user.is_admin:
                raise GraphQLError('insufficient permission')
            user = UserModel.query.filter_by(email=email).first()
            if not email:
                raise GraphQLError('user does not exist')

        db.session.delete(user)
        db.session.commit()
        success = True

        return DeleteUser(user=user, success=success)


class UpdateUser(gp.Mutation):
    class Arguments:
        email = gp.String()
        phone = gp.String()
        first_name = gp.String()
        last_name = gp.String()
        password = gp.String()

    success = gp.Boolean()
    user = gp.Field(lambda: User)

    @jwt_required()
    def mutate(root_value, info, **kwargs):
        user = current_user
        if kwargs.get('email'):
            if not current_user.is_admin:
                raise GraphQLError('insufficient permission')
            user = UserModel.query.filter_by(email=kwargs.get('email')).first()
            if not user:
                raise GraphQLError('user does not exists')

        user.phone = kwargs.get('phone', user.phone)
        user.first_name = kwargs.get('first_name', user.first_name)
        user.last_name = kwargs.get('last_name', user.last_name)

        db.session.add(user)
        db.session.commit()

        success = True

        return UpdateUser(user=user, success=success)


class Login(gp.Mutation):
    class Arguments:
        email = gp.String()
        password = gp.String()

    access_token = gp.String()
    refresh_token = gp.String()

    def mutate(root_value, info, email, password):
        user = UserModel.query.filter_by(email=email).first()

        if not user or not user.verify_password(password):
            raise GraphQLError('invalid email')

        return Login(
            access_token=create_access_token(email),
            refresh_token=create_refresh_token(email),
        )


class RefreshToken(gp.Mutation):
    access_token = gp.String()

    @jwt_required(refresh=True)
    def mutate(root_value, _):
        user = get_jwt_identity()
        return RefreshToken(access_token=create_access_token(user))


class SendMessage(gp.Mutation):
    class Arguments:
        destination = gp.String()
        message = gp.String()

    conversation = gp.Field(lambda: Conversation)

    @jwt_required()
    def mutate(root_value, info, message, destination=None):
        sender = current_user
        if '@' in destination:
            receiver = UserModel.query.filter_by(email=destination).first()
            c = sender.start_personal_chat(receiver)
            sender.send_message(c, message)
        elif destination.isnumeric():
            c = sender.start_multiperson_chat(int(destination))
            sender.send_message(c, message)
        return SendMessage(conversation=c)


class CreateMPC(gp.Mutation):
    class Arguments:
        mpc_name = gp.String()

    conversation = gp.Field(lambda: Conversation)

    @jwt_required()
    def mutate(root_value, info, mpc_name=None):
        c = current_user.start_multiperson_chat(name=mpc_name)
        return CreateMPC(conversation=c)


class AddToMPC(gp.Mutation):
    class Arguments:
        email = gp.String()
        mpc_id = gp.Int()

    conversation = gp.Field(lambda: Conversation)

    @jwt_required()
    def mutate(root_value, info, email, mpc_id):
        mpc = ConversationModel.query.get(mpc_id)
        if not mpc:
            raise GraphQLError('conversation does not exist')

        if current_user != mpc.creator:
            raise GraphQLError('you are not the creator')
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            raise GraphQLError('user does not exist')

        if mpc.title.startswith('pc'):
            mpc = current_user.start_multiperson_chat()

        mpc.add_user_to_mpc(user)
        return AddToMPC(conversation=mpc)


class AddContact(gp.Mutation):
    class Arguments:
        email = gp.String()

    contacts = gp.List(User)

    @jwt_required()
    def mutate(root_value, info, email):
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            raise GraphQLError('user does not exists')
        current_user.add_contact(user)
        return AddContact(contacts=current_user.contacts)


class Query(gp.ObjectType):
    hello = gp.String()
    me = gp.Field(User)
    my_chats = gp.List(Conversation)
    my_contacts = gp.List(User)
    my_personal_chats = gp.List(Conversation)
    my_multi_chats = gp.List(Conversation)
    user = gp.Field(User, email=gp.String())
    users = gp.List(User)
    conversation = gp.Field(Conversation, title=gp.String())
    conversations = gp.List(Conversation)

    def resolve_hello(root_value, info):
        return 'hello'

    @jwt_required()
    def resolve_me(root_value, info):
        return current_user

    @jwt_required()
    def resolve_my_chats(root_value, info):
        return current_user.participates.all()

    @jwt_required()
    def resolve_my_contacts(root_value, info):
        return current_user.contacts

    @jwt_required()
    def resolve_my_personal_chats(root_value, info):
        return current_user.participates.filter(ConversationModel.title.startswith('pc')).all()

    @jwt_required()
    def resolve_my_multi_chats(root_value, info):
        return current_user.participates.filter(ConversationModel.title.startswith('mpc')).all()

    @admin_required()
    def resolve_user(root_value, info, email):
        return UserModel.query.filter_by(email=email).first()

    @admin_required()
    def resolve_users(root_value, info):
        return UserModel.query.all()

    @admin_required()
    def resolve_conversation(root_value, info, title):
        return ConversationModel.query.filter_by(title=title).first()

    @admin_required()
    def resolve_conversations(root_value, info):
        return ConversationModel.query.all()


class Mutation(gp.ObjectType):
    login = Login.Field()
    refresh = RefreshToken.Field()
    register = CreateUser.Field()
    delete_user = DeleteUser.Field()
    update_user = UpdateUser.Field()
    send_message = SendMessage.Field()
    add_to_mpc = AddToMPC.Field()
    create_mpc = CreateMPC.Field()
    add_contact = AddContact.Field()


schema = gp.Schema(
    query=Query,
    mutation=Mutation
)
