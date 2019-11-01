import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from .models import Actor, Movie

# Create a Graphql type for actor model


class ActorType(DjangoObjectType):
    class Meta:
        model = Actor

# Create graphql type for movie model


class MovieType(DjangoObjectType):
    class Meta:
        model = Movie

# Create Query type


class Query(ObjectType):
    """ Note that each property in the Query Class corresponds
        To a graphQL query

        actor & movie return one value of Actortype and MovieType
        and require an ID...

        actors and movies properties return a list of reapective
        types

        resolvers connect queries in schema to actual actions done
        by database
    """

    actor = graphene.Field(ActorType, id=graphene.Int())
    movie = graphene.Field(MovieType, id=graphene.Int())
    actors = graphene.List(ActorType)
    movies = graphene.List(MovieType)

    def resolve_actor(self, info, **kwargs):
        id = kwargs["id"]
        if id is not None:
            return Actor.objects.get(pk=id)

    def resolve_movie(self, info, **kwargs):
        id = kwargs["id"]
        if id is not None:
            return Movie.objects.get(pk=id)

    def resolve_actors(self, info, **kwargs):
        return Actor.objects.all()

    def resolve_movies(self, info, **kwargs):
        return Movie.objects.all()

# """ MAKING MUTATIONS """
# Mutations are used for changing data in database and API
# mutation classname is what shows up as graphql name mutation

# Create Input Object Types
# These are simple classes that define what fields
# can be used to change data in the API

# Step 1: Create input Types
# Step 2: reference input types in actual mutation


class ActorInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()


class MovieInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    actors = graphene.List(ActorInput)
    year = graphene.Int()

# Create Mutations
# createActor(input: ActorInput) : ActorPayload


class CreateActor(graphene.Mutation):
    class Arguments:
        input = ActorInput(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, input=None):
        print("Info variable", info)
        print("Root variable", root)
        ok = True
        actor = Actor(name=input.name)
        actor.save()
        return CreateActor(ok=ok, actor=actor)


# updateActor(id:Int,input: ActorInput) : ActorPayload
class UpdateActor(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ActorInput(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        actor = Actor.objects.get(pk=id)
        if actor:
            ok = True
            actor.name = input.name
            actor.save()
            return UpdateActor(ok=ok, actor=actor)
        return UpdateActor(ok=ok, actor=None)

# Creating mutations for movies


class CreateMovie(graphene.Mutation):
    class Arguments:
        input = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        actors = []
        for actor_input in input.actors:
            actor = Actor.objects.get(pk=actor_input.id)
            if actor is None:
                return CreateMovie(ok=False, movie=None)
            actors.append(actor)
        movie = Movie(
            title=input.title,
            year=input.year
        )
        movie.save()
        movie.actors.set(actors)
        return CreateMovie(ok=ok, movie=movie)


class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        movie = Movie.objects.get(pk=id)
        if movie:
            ok = True
            actors = []
            for actor_input in input.actors:
                actor = Actor.objects.get(pk=actor_input.id)
                if actor is None:
                    return UpdateMovie(ok=False, movie=None)
                actors.append(actor)
            movie.title = input.title
            movie.year = input.year
            movie.save()
            movie.actors.set(actors)
            return UpdateMovie(ok=ok, movie=movie)
        return UpdateMovie(ok=ok, movie=None)


class DeleteMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    response = graphene.String()

    @staticmethod
    def mutate(root, info, id):
        ok = False
        movie = Movie.objects.get(pk=id)
        if movie:
            movie.delete()
            ok = True
            return DeleteMovie(
                ok=ok, response="Successfully deleted")
        return DeleteMovie(
            ok=ok, response="An error occured while deleting movie")


class Mutation(graphene.ObjectType):
    create_actor = CreateActor.Field()
    update_actor = UpdateActor.Field()
    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
