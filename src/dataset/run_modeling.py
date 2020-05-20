import modeling



def main():

    # this is the order of the arguments ---> run_model(num_of_epochs, train_size, test_size, batch_Size, model_number, filters, dropout, model_number)
    model_name = "words_model_1"
    print("-----------------------------------------------------------------")
    print("------------------------------------------------------------------")
    print(model_name)
    modeling.run_model(100, train_size=66000, test_size=33000, batch_Size=500, filters=8, dropout=0.1, kernel=7, model_number=model_name)


if __name__ == '__main__':
        main()
